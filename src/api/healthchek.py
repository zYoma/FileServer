import asyncio
import pickle
import time
from functools import reduce

import sqlalchemy as sa
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from cache.redis import redis_cache
from db.db import RO_ENGINE, RW_ENGINE

router = APIRouter()


@router.get(
    "/",
    summary="Проверка работоспособности сервиса",
)
async def healthcheck():
    tests = await asyncio.gather(
        check_db(RO_ENGINE, 'db_ro'),
        check_db(RW_ENGINE, 'db_rw'),
        check_redis(),
    )
    data = reduce(update, tests, {})
    return JSONResponse(status_code=200, content=data)


def update(d, other):
    d.update(other)
    return d


async def check_db(db, name: str) -> dict:
    result = {name: ''}
    try:
        start_time = time.monotonic()
        async with db.connect() as conn:
            q = await conn.scalar(sa.text("SELECT 1 -- healthcheck"))
        end_time = time.monotonic() - start_time

        result[name] = str(end_time) if 1 == q else ''
    except Exception as e:
        result[name] = str(e)
    return result


async def check_redis() -> dict:
    test_value = "Test"
    try:
        start_time = time.monotonic()
        cached = pickle.dumps(test_value)
        await redis_cache.set(name="cache_is_working_test", value=cached, ex=2)  # type: ignore
        get_value = await redis_cache.get("cache_is_working_test")  # type: ignore
        end_time = time.monotonic() - start_time
        cache_is_working = str(end_time) if pickle.loads(
            get_value) == test_value else False
    except Exception as e:
        cache_is_working = str(e)
    return {"redis": cache_is_working}
