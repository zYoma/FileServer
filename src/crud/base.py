"Реализация crud для sqlalhemy."""
import logging
from abc import abstractmethod
from collections.abc import AsyncIterator
from functools import cached_property
from typing import Any, Protocol

from sqlalchemy import Table, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ColumnOperators

from schemas.base import BaseModel

from .abc.postgres import Postgres

logger = logging.getLogger(__name__)


class BaseCrud:
    """Базовый CRUD. Будет использоваться как зависимость. Конкретные классы
    должны определить атрибуты:

       model - модель базы данных
       schema - pydantic схема объекта
       create_schema - схема без поля id

    Примеры использования:
    fond: FondRepository = Depends(),

    await fond.get_all()
    await fond.get_by_id(id=2)
    await fond.create(data=FondInSchema(comarch_id=11331, mobile_id='Vera'))
    await fond.delete(id=19)
    await fond.update(data=FondSchema(id=23, comarch_id=113317, mobile_id='Vera4'))
    """
    schema: type[BaseModel]
    id_name: str = 'id'

    @abstractmethod
    async def get_by_id(self, id: Any) -> BaseModel | None:
        ...

    @abstractmethod
    async def create(self, data: BaseModel) -> BaseModel:
        ...

    @abstractmethod
    async def update(self, id: Any, data: BaseModel) -> BaseModel:
        ...

    @abstractmethod
    async def delete(self, id: Any) -> BaseModel | None:
        ...

    @abstractmethod
    async def get(
        self,
        limit: int = None,
        offset: int = None,
        order_by: Any = None,
        **kwargs,
    ) -> AsyncIterator[BaseModel]:
        yield BaseModel()

    async def get_one(self, **kwargs) -> BaseModel | None:
        iter = self.get(limit=1, **kwargs)
        try:
            return await anext(iter)
        except StopAsyncIteration:
            return None


class BaseSqlalchemyModel(Protocol):
    __tablename__: str
    __table__: Table
    __table_args__: tuple[Any, ...]


class SqlalchemyCrud(BaseCrud, Postgres):
    model: type[BaseSqlalchemyModel]

    @cached_property
    def model_columns(self):
        from utils.functools import sqlalchemy_model_columns
        return sqlalchemy_model_columns(self.model)

    async def get_by_id(self, id: Any) -> BaseModel | None:
        query = select(self.model).where(getattr(self.model, self.id_name) == id)

        async with self.ro_session() as session:
            result = await session.execute(query)
            obj = result.scalars().first()
            return self.schema.from_orm(obj) if obj else None

    async def create(self, data: BaseModel, rw_session: AsyncSession = None) -> BaseModel:
        query = insert(self.model).values(**data.dict(exclude_defaults=True)).returning(*self.model_columns)
        async with self.rw_session() as session:
            # если нужна атомарность, создаем в рамках переданной сессии
            session = rw_session if rw_session else session

            instance = (await session.execute(query)).fetchone()
            return self.schema.from_orm(instance)

    async def update(self, id: Any, data: BaseModel) -> BaseModel:
        _d = data.dict(exclude_unset=True)
        query = update(self.model).values(**_d).where(getattr(self.model,
                                                              self.id_name) == id).returning(*self.model_columns)
        async with self.rw_session() as session:
            resp = (await session.execute(query)).fetchone()
            return self.schema.from_orm(resp)

    async def delete(self, id: Any) -> BaseModel | None:
        query = delete(self.model).where(getattr(self.model, self.id_name) == id).returning(*self.model_columns)

        async with self.rw_session() as session:
            resp = (await session.execute(query)).fetchone()
            if resp is None:
                return None
            return self.schema.from_orm(resp)

    async def get(
        self,
        limit: int = None,
        offset: int = None,
        order_by: list[ColumnOperators] = None,
        **kwargs,
    ) -> AsyncIterator[BaseModel]:
        """Позволяет получить выборку по фильтру. Фильтрует по полям полученным в kwargs."""
        query = select(self.model)
        for attr, value in kwargs.items():
            query = query.where(getattr(self.model, attr) == value)

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        if order_by:
            for ord in order_by:
                query = query.order_by(ord)

        async with self.ro_session() as session:
            result = await session.stream(query)
            async for obj in result.scalars():
                yield self.schema.from_orm(obj)
