import re
import uuid

from pydantic import validator

from schemas.base import BaseModel, IdSchema


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class CreateUser(BaseModel):
    username: str
    password: str

    @validator('username', always=True)
    def validate_username(cls, value):
        clear_username = re.sub(r'\W+', '', value)
        if value != clear_username:
            raise ValueError('username не должен содержать специальных символов!')

        return value


class User(CreateUser, IdSchema):
    ...


class FolderData(BaseModel):
    used: int
    files: int


class Folder(BaseModel):
    __root__: dict[str, FolderData] | None


class Info(BaseModel):
    account_id: uuid.UUID
    home_folder_id: uuid.UUID | None


class UserStatus(BaseModel):
    info: Info
    folders: list[Folder]
