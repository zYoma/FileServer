"""Доп функции для fastapi."""
import logging.config

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse as FastAPIResponse

from config import settings
from schemas.base import dumps
from utils.exc import UnexpectedError, exception_handler


class JSONResponse(FastAPIResponse):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return dumps(content, to_bytes=True)  # type: ignore


def configure_app() -> FastAPI:
    """Формируем FastAPI app с вещами которые обычно используем в сервисах. """
    app = FastAPI(
        title=settings.SVC_NAME or "API",
        version=settings.SVC_VERSION or "latest",
        responses={"5XX": {
            "model": UnexpectedError.schema()
        }},
        default_response_class=JSONResponse,
    )
    logging.config.dictConfig(settings.LOG.config)
    app.exception_handler(Exception)(exception_handler)
    app.exception_handler(HTTPException)(exception_handler)

    return app
