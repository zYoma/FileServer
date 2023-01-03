"""Зависимости, отвечающие за авторизацию, получение и валидацию токена пользователя."""
from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from cache.redis import timed_cache
from cache.redis_keys import all_keys
from config import settings
from crud.user import UserCrud
from schemas.user import TokenData, User
from utils.exc import AuthError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


def verify_password(plain_password: str, hashed_password: str):
    """ Проверяет, что хеш от plain_password равен hashed_password. """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """Получаем хеш пароля."""
    return pwd_context.hash(password)


async def get_user(username: str, user_crud: UserCrud) -> User | None:
    return await user_crud.get_one(username=username)  # type: ignore


async def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_crud: UserCrud = Depends(),
) -> User | bool:
    """Аунтификация пользователя."""
    user = await get_user(username=form_data.username, user_crud=user_crud)
    if not user:
        return False
    if not verify_password(form_data.password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.HASH_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_crud: UserCrud = Depends(),
) -> User:
    """Зависимость, вернет пользователя если токен валиден."""
    cache_key = all_keys.get_current_user.substitute(token=token)

    @timed_cache(cache_key=cache_key, time=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    async def cached(*args, **kwargs):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise AuthError
            token_data = TokenData(username=username)
        except JWTError:
            raise AuthError
        user = await get_user(username=token_data.username, user_crud=user_crud)
        if user is None:
            raise AuthError
        return user

    return await cached()  # type: ignore
