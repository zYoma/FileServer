import uuid
from datetime import datetime

from schemas.base import BaseModel, IdSchema


class DirectoryCreate(BaseModel):
    name: str
    user_id: uuid.UUID
    parent_id: uuid.UUID | None = None


class Directory(DirectoryCreate, IdSchema):
    created_ad: datetime
