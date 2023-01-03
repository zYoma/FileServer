"""Абстрактный класс для asyncpg."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from db.db import RO_ENGINE, RW_ENGINE
from db.sqlalchemy.asyncpg import make_sessionmaker, session


class Postgres:
    """Работа с postgres.

    Attributes:
        rw_engine (AsyncEngine): engine для read write операций
        ro_engine (asyncEngine): engine для read операций
    """
    rw_engine: AsyncEngine = RW_ENGINE
    ro_engine: AsyncEngine | None = RO_ENGINE

    def __init__(self):
        if self.ro_engine is None:
            self.ro_engine = self.rw_engine

    @asynccontextmanager
    async def rw_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекст менеджер для получения read/write сессии.

        Examples:

            async with db.rw_sesstion() as s:
                await s.execute(text('select 1'))
        """
        async with session(make_sessionmaker(self.rw_engine)) as s:
            yield s

    @asynccontextmanager
    async def ro_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекст менеджер для получения read сессии.

        Examples:

            async with db.ro_sesstion() as s:
                await s.execute(text('select 1'))
        """
        async with session(make_sessionmaker(self.ro_engine)) as s:
            yield s
