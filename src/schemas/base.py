import enum
import traceback
import uuid
from datetime import date, datetime, time
from functools import cached_property
from inspect import istraceback

import orjson
import pytz
from pydantic import BaseModel as DefaultModel


def default_dumps(obj):
    if istraceback(obj):
        return "".join(traceback.format_tb(obj)).strip()

    if isinstance(obj, (date, time)):
        return obj.isoformat()

    if isinstance(obj, enum.Enum):
        return obj.value

    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            return obj.astimezone(pytz.UTC).isoformat()
        return obj.astimezone().isoformat()

    return str(obj)


def dumps(data, **kwargs) -> str | bytes:
    to_bytes = kwargs.pop("to_bytes", False)
    _json = orjson.dumps(
        data,
        default=kwargs.pop("default", default_dumps),
        option=orjson.OPT_SERIALIZE_UUID | orjson.OPT_NAIVE_UTC,
    )
    if to_bytes:
        return _json
    return _json.decode("utf-8")


def loads(data, **kwargs):
    return orjson.loads(data)


class BaseModel(DefaultModel):

    class Config:
        json_dumps = dumps
        json_loads = loads
        keep_untouched = (cached_property, property)
        allow_population_by_field_name = True
        orm_mode = True
        underscore_attrs_are_private = True


class IdSchema(BaseModel):
    id: uuid.UUID
