"""Base for all models.

It has some type definitions to enhance autocompletion.
"""
from typing import Any

import sqlalchemy as sa
from sqlalchemy import Table
from sqlalchemy.orm import as_declarative

meta = sa.MetaData()


@as_declarative(metadata=meta)
class Base:
    """Base for all models.

    It has some type definitions to enhance autocompletion.
    """

    __tablename__: str
    __table__: Table
    __table_args__: tuple[Any, ...]
