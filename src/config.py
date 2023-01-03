"""Настройки проекта."""
import enum
from functools import cached_property

from pydantic import BaseSettings, Field

from utils.logs import get_log_config


class LogLevel(enum.Enum):
    """Возвомжные уровеня логирования."""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class PostgresSettings(BaseSettings):
    """Настройки Postgres."""

    RW_DSN: str = Field(description='DSN мастер БД')
    RO_DSN: str = Field(None, description='DSN реплика БД')
    TEST_DSN: str = Field(None, description='DSN для тестов')
    PASSWORD: str = Field('postgres', description='Пароль подключения к серверу БД')
    CONNECT_TIMEOUT: float = Field(5.0, description='Таймаут коннекта к БД', example='5.0')
    COMMAND_TIMEOUT: int | None = Field(None, description='Таймаут операций', example='60')
    POOL_SIZE: int = Field(5, description='Размер пула соединений к БД', example='5')
    POOL_RECYCLE: int = Field(60, description='Время жизни соединения к БД для пула соединений', example='60')
    POOL_TIMEOUT: float = Field(60, description='Таймаут для получения нового соединения из пула', example='60')

    @cached_property
    def rw_dsn(self):
        return self.RW_DSN

    @cached_property
    def ro_dsn(self):
        if not self.RO_DSN:
            return self.rw_dsn
        return self.RO_DSN

    class Config:
        keep_untouched = (cached_property, property)


class LogSettings(BaseSettings):
    """Настройки для логов."""
    LOG_LEVEL: LogLevel = Field(LogLevel.INFO, description="Уровень логирования")
    DB_LEVEL: LogLevel = Field(LogLevel.CRITICAL, description="Уровень логирования для запросов к бд")
    SQL_ECHO: bool = Field(False, description='логирование sql запросов')

    @cached_property
    def config(self) -> dict:
        """Конфиг для logging.dictConfig.

        Returns:
            dict: словарь допустимый logging.dictConfig
        """

        return get_log_config(self)  # type: ignore

    class Config:
        keep_untouched = (cached_property, property)


class Settings(BaseSettings):
    """Все настройки."""

    POSTGRES: PostgresSettings = PostgresSettings()
    REDIS_DSN: str = Field('redis://redis:6379/1', description='dsn для подключения к кэшу redis')

    SVC_VERSION: str = Field("latest", description="версия приложения")
    SVC_NAME: str = Field("file_server", description="название приложения")
    STATIC_ROOT: str = Field("static/", description="каталог для хранения статических файлов")
    MAX_FILE_SIZE_KB: int = Field(1024, description="максимальный размер загружаемого файла")

    LOG: LogSettings = LogSettings()
    SECRET_KEY: str = Field(description='секретный ключ приложения')
    HASH_ALGORITHM: str = Field("HS256", description='алгоритм шифрования пароля')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description='срок жизни токена в минутах')


settings = Settings()
