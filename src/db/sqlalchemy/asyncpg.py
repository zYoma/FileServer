"""Asyncpg session makers."""
import logging
from contextlib import asynccontextmanager
from enum import Enum
from functools import lru_cache

from asyncpg import connect
from asyncpg.connect_utils import _parse_connect_dsn_and_args
from asyncpg.connection import Connection
from sqlalchemy import event
from sqlalchemy.dialects.postgresql.asyncpg import \
    AsyncAdapt_asyncpg_connection
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util.concurrency import await_only

logger = logging.getLogger("db")


@asynccontextmanager
async def session(maker: sessionmaker) -> AsyncSession:
    """Контекст менеджер для сессии.

    Args:
        maker (sassionmaker): Класс для открытия сессии
    """
    async with maker.begin() as session:
        try:
            yield session
        except Exception as e:
            logger.warning("Session %s rollback: %s", maker, e, exc_info=True)
            await session.rollback()
            raise


class IsolationLevel(str, Enum):
    """Енум для указания уровня изоляции для engine."""
    AUTOCOMMIT = "AUTOCOMMIT"
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"


@lru_cache
def get_async_engine(
    dsn: str,
    connection: type[Connection] = Connection,
    password: str = None,
    application_name: str = "",
    timeout: int | None = 5,
    statement_cache_size: int = 100,
    max_cached_statement_lifetime: int = 300,
    max_cacheable_statement_size: int = 1024 * 15,
    command_timeout: int | None = None,
    pool_size: int = 5,
    pool_recycle: int = 60,
    pool_timeout: int = 30,
    max_overflow: int = 0,
    **engine_kwargs,
) -> AsyncEngine:
    """Формируем `AsyncEngine`.

    Args:
        dsn (str): dsn по которому коннектимся
        connection (type[Connection]): Класс коннекта по умолчанию `Connection`
        password (str): пароль
        application_name (str): название приложение будет прокидываться в server_settings
        timeout (int | None): таймаут коннекта
        statement_cache_size (int): размер кэша для prepared запросов по умолчанию 100,
        max_cached_statement_lifetime (int): время жизни кэша для запросов по умолчанию 300,
        max_cacheable_statement_size (int): максимальынй размер запроса для кэша по умолчанию 1024 * 15
        command_timeout (int | None): таймаут при запросе по умолчанию None
        pool_size (int): размер пула
        pool_recycle (int): через сколько секунд не используемого коннекта вернуть в пул по умолчанию 60
        pool_timeout (int): таймаут ожидания коннекта из пулла по умолчанию 30
        max_overflow (int): на сколько можно привысить размер пула по умолчанию 0
        **engine_kwargs: остальные аргументы для `create_async_engine`
    """
    engine = create_async_engine(
        "postgresql+asyncpg://",
        pool_size=pool_size,
        pool_recycle=pool_recycle,
        pool_timeout=pool_timeout,
        max_overflow=max_overflow,
        **engine_kwargs,
    )

    if not isinstance(dsn, str):
        dsn = str(dsn)

    dsn = dsn.replace("+asyncpg", "")

    @event.listens_for(engine.sync_engine, "do_connect")
    def receive_do_connect(dialect, conn_rec, cargs, cparams):
        server_settings = cparams.get("server_settings", {
            "application_name": application_name,
        })
        return AsyncAdapt_asyncpg_connection(
            dialect.dbapi,
            await_only(
                connect(
                    dsn,
                    timeout=timeout,
                    connection_class=connection,
                    password=password,
                    command_timeout=command_timeout,
                    statement_cache_size=statement_cache_size,
                    max_cached_statement_lifetime=max_cached_statement_lifetime,
                    max_cacheable_statement_size=max_cacheable_statement_size,
                    server_settings=server_settings,
                )))

    return engine


@lru_cache
def make_sessionmaker(
    engine: AsyncEngine,
    autoflush=True,
    autocommit=False,
    expire_on_commit=False,
    info=None,
    isolation: IsolationLevel = IsolationLevel.READ_COMMITTED,
    **execution_options,
) -> sessionmaker:
    return sessionmaker(
        engine.execution_options(isolation_level=isolation.value, **execution_options),
        expire_on_commit=expire_on_commit,
        info=info,
        autocommit=autocommit,
        autoflush=autoflush,
        class_=AsyncSession,
    )


def get_alembic_dsn(
    *,
    dsn=None,
    host=None,
    port=None,
    user=None,
    password=None,
    passfile=None,
    ssl=None,
    database=None,
    connect_timeout=None,
    server_settings=None,
    direct_tls=None,
) -> str:
    """берем только 1 ноду."""
    dsn = dsn.replace("+asyncpg", "")
    addrs, cfg = _parse_connect_dsn_and_args(
        dsn=dsn,
        host=host,
        port=port,
        user=user,
        password=password,
        passfile=passfile,
        ssl=ssl,
        database=database,
        connect_timeout=connect_timeout,
        server_settings=server_settings,
        direct_tls=direct_tls,
    )
    addr = addrs[0]
    url = URL(
        drivername="postgresql+asyncpg",
        username=cfg.user,
        password=cfg.password,
        database=cfg.database,
        port=addr[1],
        host=addr[0],
    )
    return str(url)
