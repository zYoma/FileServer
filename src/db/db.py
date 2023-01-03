from config import settings

from .sqlalchemy.asyncpg import get_async_engine

pool_kwargs = dict(password=settings.POSTGRES.PASSWORD,
                   pool_size=settings.POSTGRES.POOL_SIZE,
                   pool_timeout=settings.POSTGRES.POOL_TIMEOUT,
                   command_timeout=settings.POSTGRES.COMMAND_TIMEOUT,
                   application_name=settings.SVC_NAME,
                   echo=settings.LOG.SQL_ECHO)

# Пуллы для мастера и для реплики. Создаются один раз.
RO_ENGINE = get_async_engine(settings.POSTGRES.ro_dsn, **pool_kwargs)
RW_ENGINE = get_async_engine(settings.POSTGRES.rw_dsn, **pool_kwargs)
