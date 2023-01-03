"""доп функции."""
import uuid
from functools import lru_cache

from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty


@lru_cache
def sqlalchemy_model_columns(db_model):  # pylint: disable=function-redefined
    """Получение колонок для sqlalchemy модели."""
    mapper = inspect(db_model)
    columns = []
    for attr in mapper.attrs:
        if not isinstance(attr, ColumnProperty):
            continue

        if not attr.columns:
            continue
        columns.append(attr.class_attribute)
    return columns


def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
