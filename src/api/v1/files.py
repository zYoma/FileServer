from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import StreamingResponse

from cache.redis import timed_cache
from cache.redis_keys import all_keys
from crud.file import FileCrud
from crud.revision import RevisionCrud
from db.models.file import FileOrderBy
from depends.auth import get_current_user
from schemas.file import File, SearchResult
from schemas.revision import RevisionResponse
from schemas.user import User
from services.file import DownloadFileManager, FileManager

router = APIRouter()


@router.post(
    "/upload",
    response_model=File,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить файл в хранилище",
)
async def upload_file(
    path: str,
    file: UploadFile,
    user: User = Depends(get_current_user),
):
    manager = FileManager(user)
    return await manager.save_file(path, file)


@router.get(
    "/list",
    response_model=list[File],
    summary="Получить список файлов",
)
async def get_list_file(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    file_crud: FileCrud = Depends(),
):
    cache_key = all_keys.file_list.substitute(user_id=user.id)

    @timed_cache(cache_key=cache_key, time=5 * 60)
    async def cached(*args, **kwargs):
        return [file async for file in file_crud.get(user_id=user.id, limit=limit, offset=offset)]

    return await cached()  # type: ignore


@router.get(
    "/download",
    summary="Скачать файл или директорию",
)
async def download_file(
    path: str,
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    manager = DownloadFileManager(user)
    return await manager.get_file_or_directory(path)


@router.get(
    "/search",
    response_model=SearchResult,
    summary="Поиск файлов",
)
async def search_files(
    path: str | None = None,
    extension: str | None = None,
    order_by: FileOrderBy = FileOrderBy.created_ad,
    limit: int = 100,
    user: User = Depends(get_current_user),
    file_crud: FileCrud = Depends(),
) -> SearchResult:

    cache_key = all_keys.search_files.substitute(
        user_id=user.id,
        path=path,
        extension=extension,
        order_by=order_by,
        limit=limit,
    )

    @timed_cache(cache_key=cache_key, time=5 * 60)
    async def cached(*args, **kwargs):
        file_list = [
            file
            async for file in file_crud.search(
                user_id=user.id,
                path=path,
                extension=extension,
                order_by=order_by,
                limit=limit
            )
        ]
        return SearchResult(**{"matches": file_list})

    return await cached()  # type: ignore


@router.get(
    "/revisions",
    response_model=list[RevisionResponse],
    summary="Информацию о изменениях файла",
)
async def revision_files(
    path: str,
    limit: int = 100,
    user: User = Depends(get_current_user),
    revision_crud: RevisionCrud = Depends(),
) -> list[RevisionResponse]:

    cache_key = all_keys.revision_files.substitute(
        user_id=user.id,
        path=path,
        limit=limit,
    )

    @timed_cache(cache_key=cache_key, time=5 * 60)
    async def cached(*args, **kwargs):
        return await revision_crud.get_revision(path=path, user_id=user.id, limit=limit)

    return await cached()  # type: ignore
