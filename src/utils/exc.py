"""Опеределяем как кработаем с эксепшенами."""
import enum
import logging

from fastapi import HTTPException, Request, status
from pydantic import Field, create_model

from config import settings
from schemas.base import BaseModel

logger = logging.getLogger('exceptions')


async def exception_handler(request: Request, exc: Exception):
    from utils.helpers import JSONResponse
    logger.exception(exc,
                     extra={
                         'exc': exc.__class__.__name__,
                         'exc_args': str(exc.args),
                         'error_message': getattr(exc, 'error_message', ''),
                         'public_message': getattr(exc, 'public_message', ''),
                     })

    if not isinstance(exc, HTTPException):
        exc = UnexpectedError(exc)

    if 200 <= exc.status_code <= 300:
        exc.status_code = 400

    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.detail},
        headers={
            'access-control-allow-origin': '*',
        },
    )


class ErrorCodes(enum.IntEnum):
    UNDEFINED_ERROR = 1
    UNAUTHORIZED_ERROR = 2
    FORBIDDEN_ERROR = 3
    INTERNAL_SERVER_ERROR = 4
    VALIDATION_ERROR = 5
    NOT_FOUND = -1


class DetailSchema(BaseModel):
    code: str = Field(..., description='Код ошибки')
    message: str = Field(..., description='Публичное сообщение об ошибке')
    error: str = Field('', description='Подробное сообщение об ошибке, вызывается при LOG__LEVEL == DEBUG')


class BaseServiceException(HTTPException):
    """Базовый класс для ошибок."""
    status_code = 500
    code: ErrorCodes = ErrorCodes.UNDEFINED_ERROR
    message: str = 'Unexcepted'

    def __init__(self, public_message='', error_message='') -> None:
        if public_message and isinstance(public_message, str):
            self.message = public_message

        if error_message and isinstance(error_message, str):
            self.error_message = error_message
        if not isinstance(error_message, str) or not logger.isEnabledFor(logging.DEBUG):
            error_message = ''
        super().__init__(
            status_code=self.status_code,
            detail={
                'code': self.code.name,
                'message': self.message,
                'error': error_message
            },
        )

    _schema_cached: dict[str, BaseModel] = {}

    @classmethod
    def schema(cls):
        if cls.__name__ in cls._schema_cached:
            return cls._schema_cached[cls.__name__]
        sch = create_model(
            cls.__name__,
            detail=(DetailSchema, DetailSchema(code=cls.code.name, message=cls.message)),
            __base__=BaseModel,
        )
        cls._schema_cached[cls.__name__] = sch
        return sch


class UnexpectedError(BaseServiceException):

    def __init__(self, original: Exception = None) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            super().__init__(error_message=repr(original))
        else:
            super().__init__()


class NotFoundError(BaseServiceException):
    status_code = 404
    code = ErrorCodes.NOT_FOUND
    message = 'Not Found'


class TimeoutError(BaseServiceException):
    status_code = 504
    message = 'Try later'


class AuthError(BaseServiceException):
    status_code = 401
    code = ErrorCodes.UNAUTHORIZED_ERROR
    message = 'Not authenticated'


class ForbiddenError(BaseServiceException):
    status_code = 403
    code = ErrorCodes.FORBIDDEN_ERROR
    message = 'Forbidden'


class InternalServerError(BaseServiceException):
    status_code = 500
    code = ErrorCodes.INTERNAL_SERVER_ERROR
    message = 'Internal Server Error'


class ValidationError(BaseServiceException):
    status_code = 400
    code = ErrorCodes.VALIDATION_ERROR
    message = 'Invalid'


class BadUserNameError(BaseServiceException):
    status_code = 400
    code = ErrorCodes.VALIDATION_ERROR
    message = 'Указанное имя пользователя занято'


class LargeFileError(BaseServiceException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    code = ErrorCodes.VALIDATION_ERROR
    message = f'Размер файла не должен превышать {settings.MAX_FILE_SIZE_KB} kb'
