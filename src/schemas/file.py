import uuid
from datetime import datetime

from schemas.base import BaseModel, IdSchema


class FileCreate(BaseModel):
    name: str
    path: str
    size: int
    user_id: uuid.UUID
    created_ad: datetime
    directory_id: uuid.UUID


class File(FileCreate, IdSchema):
    ...


class UploadFileBody(BaseModel):
    path: str


class SearchResult(BaseModel):
    matches: list[File]


class ViewFile(IdSchema):
    content: str
