import logging
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from crud.base import SqlalchemyCrud
from crud.revision import RevisionCrud
from db.models.file import File, FileOrderBy
from schemas.base import BaseModel
from schemas.file import File as FileSchema
from schemas.revision import RevisionCreate
from utils.functools import is_valid_uuid

logger = logging.getLogger(__name__)


class FileCrud(SqlalchemyCrud):
    model: type[File] = File   # type: ignore
    schema = FileSchema

    async def create_or_update(self, data: BaseModel, file_hash: str) -> FileSchema:
        query = insert(self.model).values(**data.dict(exclude_defaults=True)).on_conflict_do_update(
            constraint='uix_name_directory_id',
            set_=data.dict(exclude_defaults=True),
        ).returning(*self.model_columns)

        async with self.rw_session() as session:
            instance = (await session.execute(query)).fetchone()
            file = self.schema.from_orm(instance)
            # важно атомарно создать ревизию файла в рамках той же сессии
            # если не удастся создать ревизию, то и файл  не должен сохранится
            revision = RevisionCreate(hash=file_hash, file_id=file.id)
            try:
                await RevisionCrud().create(data=revision, rw_session=session)
            except IntegrityError:
                logger.info("Ревизия для данного файла уже существует.")
            return file

    async def search(self, user_id: uuid.UUID, path: str, extension: str, order_by: FileOrderBy, limit: int):
        # все файлы пользователя
        query = select(self.model).where(self.model.user_id == user_id)
        # фильтр по path
        if path:
            if is_valid_uuid(path):
                query = query.where(self.model.id == path)
            else:
                query = query.where(self.model.path == path)

        # фильтр по расширению
        if extension:
            query = query.where(self.model.name.ilike(f'%.{extension}%'))

        if limit:
            query = query.limit(limit)

        # сортировка
        query = query.order_by(order_by)

        async with self.ro_session() as session:
            result = await session.stream(query)
            async for obj in result.scalars():
                yield self.schema.from_orm(obj)
