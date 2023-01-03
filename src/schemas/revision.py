import uuid
from datetime import datetime

from schemas.base import BaseModel, IdSchema


class RevisionCreate(BaseModel):
    hash: str
    file_id: uuid.UUID


class Revision(RevisionCreate, IdSchema):
    modified_at: datetime


class RevisionResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_ad: datetime
    path: str
    rev_id: uuid.UUID
    hash: str
    modified_at: datetime
