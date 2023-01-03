import hashlib
import logging
import os
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO

import aiofiles
from aiofiles import os as aio_os
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError

from config import settings
from crud.directory import DirectoryCrud
from crud.file import FileCrud
from crud.revision import RevisionCrud
from schemas.directory import DirectoryCreate
from schemas.file import File, FileCreate
from schemas.user import User
from utils.exc import LargeFileError, NotFoundError
from utils.functools import is_valid_uuid

logger = logging.getLogger(__name__)


@dataclass
class FileManager:
    """Менеджер пользовательских директорий."""
    user: User
    base_dir: str = settings.STATIC_ROOT

    directory_crud: DirectoryCrud = DirectoryCrud()
    file_crud: FileCrud = FileCrud()
    revision_crud: RevisionCrud = RevisionCrud()

    async def save_file(self, in_path: str, file: UploadFile) -> File:
        file_path, file_name = self._get_file_data(in_path, file.filename)
        full_path = os.path.join(self.base_dir, file_path)

        directory_id = await self._create_dirs(file_path)
        file_size, file_hash = await self._save_file(file, full_path)
        file_data = {
            "name": file_name,
            "path": full_path,
            "size": file_size,
            "created_ad": datetime.now(),
            "directory_id": directory_id,
            "user_id": self.user.id,
        }
        return await self._create_file(file_data, file_hash)

    async def _create_file(self, file_data: dict, file_hash: str) -> File:
        file = FileCreate(**file_data)
        return await self.file_crud.create_or_update(file, file_hash)

    def _get_file_data(self, in_path: str, file_name: str) -> tuple[str, str]:
        """ Метод для получения пути для сохранения файла и его имени."""
        # если введеный путь начинается с /, убираем его
        if in_path.startswith('/'):
            in_path = in_path[1:]

        file_path = os.path.join(self.user.username, in_path)
        if self._is_dir_path(in_path):
            # если передан путь до категории, то добавляем к нему имя загружаемого файла
            return os.path.join(file_path, file_name), file_name

        # если передан путь до фала, получаем имя файла из него
        file_name = file_path.split('/')[-1]
        return file_path, file_name

    async def _create_dirs(self, file_path: str) -> uuid.UUID | None:
        # собираем список директорий включая вложенные
        dirs = file_path.split('/')[:-1]

        parent_id = None
        parent_dir_name = ''
        for directory in dirs:
            # создаем директорию на диске
            await self._create_dir_on_disk(directory, parent_dir_name)
            # создаем директорию в БД (нужно создавать последовательно так как нужен parent_id)
            directory_model = DirectoryCreate(name=directory, user_id=self.user.id, parent_id=parent_id)
            try:
                new_directory = await self.directory_crud.create(directory_model)
            except IntegrityError:
                # если директория уже существует, получаем ее
                new_directory = await self.directory_crud.get_one(name=directory)  # type: ignore
            # только что созданная становится родительской для следующей
            parent_id = new_directory.id  # type: ignore
            parent_dir_name = os.path.join(parent_dir_name, directory)

        return parent_id

    async def _create_dir_on_disk(self, dir_name: str, parent_path: str = '') -> None:
        """Метод для создания директорий пользователя, если они не существуют."""
        path = os.path.join(parent_path, dir_name)
        full_path = os.path.join(self.base_dir, path)
        await aio_os.makedirs(full_path, exist_ok=True)

    @staticmethod
    async def _save_file(file: UploadFile, path: str) -> tuple[int, str]:
        max_file_size = settings.MAX_FILE_SIZE_KB * 1024
        real_file_size = 0
        hash_md5 = hashlib.md5()

        async with aiofiles.open(path, 'wb') as out_file:
            # читаем файл чанками
            while content := await file.read(1024):
                # проверяем фактический размер файла
                real_file_size += len(content)
                if real_file_size > max_file_size:
                    # удаляем файл, если превысил допустимый размер
                    await aio_os.remove(path)
                    raise LargeFileError
                await out_file.write(content)
                hash_md5.update(content)

        return real_file_size, hash_md5.hexdigest()

    @staticmethod
    def _is_dir_path(path: str) -> bool:
        """Метод позволяет определить по переданному пути, является ли путь до директории или до файла."""
        # если путь оканчивается на / - это путь до директории
        if path and path[-1] == '/':
            return True

        file_name = path.split('/')[-1]
        # если у последней части пути нет расширения - это путь до директории
        if len(file_name.split('.')) == 1:
            return True

        return False


@dataclass
class DownloadFileManager:
    user: User
    base_dir: str = settings.STATIC_ROOT

    directory_crud: DirectoryCrud = DirectoryCrud()
    file_crud: FileCrud = FileCrud()

    async def get_file_or_directory(self, path: str) -> StreamingResponse:
        if is_valid_uuid(path):
            # если передан идентификатор
            file_list = await self._get_file_list_by_id(path)
        else:
            # если передан путь
            file_list = await self._get_file_list_by_path(path)

        return self._zip_files(file_list)

    async def _get_file_list_for_directory(self, name: str, parent_id: uuid.UUID) -> list[str]:
        """Метод собирает абсолютные пути до всех файлов начиная с переданной директории."""
        dirs_list = await self._get_path_to_dir(name, parent_id)
        dirs_list.reverse()
        path = '/'.join(dirs_list)

        path = os.path.join(self.base_dir, path)
        file_list = []
        for root, _, files in os.walk(path):
            # если в каталоге есть файлы
            if files:
                for file in files:
                    file_list.append(os.path.join(root, file))
        return file_list

    async def _get_path_to_dir(self, dir_name: str, parent_id: uuid.UUID) -> list[str]:
        """Рекурсивно собираем названия всех директорий от корня до нужной."""
        if not parent_id:
            # базовый случай, директория корневая
            return [dir_name]

        parent = await self.directory_crud.get_one(id=parent_id)
        # уходим в рекурсию
        return [dir_name] + await self._get_path_to_dir(parent.name, parent.parent_id)  # type: ignore

    async def _get_file_list_by_id(self, id: str) -> list[str] | File:
        # пробуем найти директорию
        if directory := await self.directory_crud.get_one(id=id, user_id=self.user.id):
            return await self._get_file_list_for_directory(directory.name, directory.parent_id)  # type: ignore

        # пробуем найти файл
        if file := await self.file_crud.get_one(id=id, user_id=self.user.id):
            return file  # type: ignore

        raise NotFoundError

    async def _get_file_list_by_path(self, path: str) -> list[str] | File:
        # пробуем найти файл с переданным путем
        if file := await self.file_crud.get_one(path=path, user_id=self.user.id):
            return file  # type: ignore

        if path.endswith('/'):
            path = path[:-1]
        # пробуем найти директорию соответсвующую переданному пути
        dir_name = path.split('/')[-1]
        if directory := await self.directory_crud.get_one(name=dir_name, user_id=self.user.id):
            return await self._get_file_list_for_directory(directory.name, directory.parent_id)  # type: ignore

        raise NotFoundError

    @staticmethod
    def _zip_files(file_list: list[str] | File) -> StreamingResponse:
        io = BytesIO()
        zip_filename = "archive.zip"

        with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
            if isinstance(file_list, File):
                zip.write(file_list.path, arcname=file_list.name)
            else:
                for fpath in file_list:
                    zip.write(fpath)

        return StreamingResponse(
            iter([io.getvalue()]),
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment;filename={zip_filename}"}
        )
