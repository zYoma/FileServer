import asyncio
import os
import shutil
from datetime import timedelta
from unittest.mock import PropertyMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine

from cache.redis import redis_cache
from config import settings
from crud.abc.postgres import Postgres
from db.base import meta as metadata
from db.db import pool_kwargs
from db.models.directory import Directory
from db.models.user import User
from db.sqlalchemy.asyncpg import get_async_engine, make_sessionmaker, session
from depends.auth import create_access_token
from main import app

base_url = "http://localhost:8080"


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    """Фикстура возвращает подключение к тестовой БД."""
    yield get_test_engine()


@pytest.fixture(scope="session")
async def create(engine):
    """Создает таблицы перед тестаи и дропает их после."""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope="session")
async def test_app(engine, create):
    # Подменяем подключение к Postgres на тестовое
    Postgres.rw_engine = engine
    Postgres.ro_engine = engine

    await clear_cache()
    await fill_data()
    yield app
    await clear_cache()


async def clear_cache():
    """Чистим кеш."""
    all_keys = await redis_cache.keys()
    for key in all_keys:
        await redis_cache.delete(key.decode("utf-8"))


async def fill_data():
    """Наполняем БД нужными для тестов данными."""
    settings.MAX_FILE_SIZE_KB = 350

    engine = get_test_engine()
    async with session(make_sessionmaker(engine)) as s:
        s.add(User(username="test_user", password="$2b$12$xOEZKsTz2wykeRXaKE1Die.75pr3xjM8EYFp9L0FsK5zQMfQdg03G"))
        s.add(User(username="test_user2", password="$2b$12$xOEZKsTz2wykeRXaKE1Die.75pr3xjM8EYFp9L0FsK5zQMfQdg03G"))
        await s.commit()


def get_test_engine() -> AsyncEngine:
    return get_async_engine(settings.POSTGRES.TEST_DSN, **pool_kwargs)


def create_token(username: str):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return access_token


@pytest.fixture(scope="session")
def token1():
    access_token = create_token("test_user")
    yield f"Bearer {access_token}"


@pytest.fixture(scope="session")
def token2():
    access_token = create_token("test_user2")
    yield f"Bearer {access_token}"


@pytest.fixture(autouse=True)
def make_static_dir():
    static_dir = 'tmp/'
    os.makedirs(static_dir, exist_ok=True)
    yield static_dir
    shutil.rmtree(static_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
async def clear_dirs(engine):
    # после каждого теста будем очищать таблицу с директориями, чтобы один тест не влиял на другой
    yield
    async with session(make_sessionmaker(engine)) as s:
        await s.execute(delete(Directory))


@pytest.fixture
async def create_files(test_app, token1):
    # Фикстура будет создавать файлы для других тестов.
    # Сама работа ручки upload_file тестируется в отдельном тесте
    files = [
        ('file.txt', 'tests/mocks/test.jpg'),
        ('docs/one/two', 'tests/mocks/test.pdf'),
        ('docs/one/two/new.txt', 'tests/mocks/test.txt'),
    ]
    file_list = []
    for path, file in files:
        params = {'path': path}
        files = {'file': open(file, "rb")}
        with patch(
                "services.file.FileManager.base_dir", new_callable=PropertyMock, return_value='tmp/'
        ):
            async with AsyncClient(app=test_app, base_url=base_url, headers={'Authorization': token1}) as ac:
                response = await ac.post(test_app.url_path_for('upload_file'), params=params, files=files)
                file = response.json()
                file_list.append(file)

    yield file_list
