"""Конфиг логов."""
import enum
from typing import Protocol

try:
    import coloredlogs  # type: ignore

    coloredlogs.install()

    CONSOLE_FORMATTER = "coloredlogs.ColoredFormatter"

except ImportError:
    CONSOLE_FORMATTER = "logging.Formatter"


class LogLevel(enum.Enum):
    """Возвомжные уровеня логирования."""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class LogSettings(Protocol):
    """Интерфейс настроек для логера."""
    LOG_LEVEL: LogLevel
    DB_LEVEL: LogLevel
    SQL_ECHO: LogLevel


def get_log_config(settings: LogSettings):
    config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": settings.LOG_LEVEL.value,
            "handlers": ["stdout"],
        },
        "formatters": {
            "console": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
                "()": CONSOLE_FORMATTER,
            },
        },
        "handlers": {
            "stdout": {
                "level": settings.LOG_LEVEL.value,
                "class": "logging.StreamHandler",
                "formatter": "console",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "console",
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "level": LogLevel.ERROR.value,
                "class": "logging.StreamHandler",
                "formatter": "console",
                "stream": "ext://sys.stderr",
            },
            "null": {
                "class": "logging.NullHandler",
                "level": LogLevel.WARNING.value,
            },
        },
        "loggers": {
            "db": {
                "handlers": ["stdout"],
                "level": settings.DB_LEVEL.value,
            },
            "uvicorn": {
                "handlers": ["stdout"],
                "level": settings.LOG_LEVEL.value,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": settings.LOG_LEVEL.value,
            },
        },
    }
    if settings.SQL_ECHO:
        config["loggers"].update(
            {
                "sqlalchemy.engine.Engine": {
                    "handlers": ["null"],
                    "level": settings.DB_LEVEL.value,
                },
            }
        )

    return config
