import pickle
from logging import getLogger

from redis import Redis
from redis import asyncio as aioredis

from config import settings

logger = getLogger("redis")


def setup_redis() -> Redis:
    """
    Создаем пул соединений к редису
    :return: Redis-object
    """
    logger.debug('creating redis connection pool')
    redis = aioredis.from_url(settings.REDIS_DSN, socket_timeout=0.5)
    logger.debug('redis connection pool was created')
    return redis  # type: ignore


async def teardown_redis():
    """
    Закрываем пул соединений к редису
    """
    logger.debug('closing redis connection pool')
    # к моменту вызова teardown_redis глобальный объект redis_cache определен
    # и находится в области видимости данной функции, поэтому просто делаем:
    await redis_cache.close()
    logger.debug('redis connection pool was closed')


def timed_cache(cache_key: str, time: int):
    def wrap(func):
        async def wrapped(*args, **kwargs):
            cached_result = None
            try:
                cached_result = await redis_cache.get(cache_key)
            except TimeoutError as e:
                logger.error(str(e))
            if cached_result:
                return pickle.loads(cached_result)
            func_result = await func(*args, **kwargs)
            if func_result:
                cached = pickle.dumps(func_result)
                try:
                    await redis_cache.set(name=cache_key, value=cached, ex=time)
                except TimeoutError as e:
                    logger.error(str(e))
            return func_result

        return wrapped
    return wrap


redis_cache = setup_redis()
