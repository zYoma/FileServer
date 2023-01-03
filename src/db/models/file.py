import uuid
from enum import Enum

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from db.base import Base


class FileOrderBy(str, Enum):
    name = "name"  # type: ignore
    size = "size"
    created_ad = "created_ad"


class File(Base):
    __tablename__ = 'file'
    __table_args__ = (
        UniqueConstraint('name', 'directory_id', name='uix_name_directory_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    name = Column(String(100), nullable=False, index=True, comment='Имя файла')
    path = Column(String(500), nullable=False, unique=True, comment='Путь до файла')
    size = Column(Integer, nullable=False, comment='Размер файла')
    created_ad = Column(DateTime(timezone=True), default=func.now(),
                        nullable=False, comment='Дата добавления файла')
    directory_id = Column(UUID(as_uuid=True), ForeignKey('directory.id', ondelete="CASCADE"),
                          nullable=False, comment='Связь с директорией')
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete="CASCADE"),
                     nullable=False, comment='Связь с пользователем')
