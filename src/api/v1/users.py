from datetime import timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError

from config import settings
from crud.directory import DirectoryCrud
from crud.user import UserCrud
from depends.auth import (authenticate_user, create_access_token,
                          get_current_user, get_password_hash)
from schemas.user import CreateUser, Token, User, UserStatus
from utils.exc import AuthError, BadUserNameError

router = APIRouter()


@router.post("/auth", response_model=Token, summary="Аутентификация пользователя")
async def login_for_access_token(user: User = Depends(authenticate_user)):
    if not user:
        raise AuthError
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Регистрация пользователя")
async def register(creds: CreateUser, user: UserCrud = Depends()):
    # получаем хеш пароля
    creds.password = get_password_hash(creds.password)
    try:
        return await user.create(creds)
    except (IntegrityError, ValueError):
        raise BadUserNameError


@router.get("/status", response_model=UserStatus, summary="Статус использования дискового пространства.")
async def file_status(
    directory_crud: DirectoryCrud = Depends(),
    user: User = Depends(get_current_user),
) -> UserStatus:
    return await directory_crud.get_status(user.id)
