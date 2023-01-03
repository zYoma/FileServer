import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from db.base import Base


class Revision(Base):
    __tablename__ = 'revision'
    __table_args__ = (
        UniqueConstraint('hash', 'file_id', name='uix_hash_file_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    hash = Column(String(500), nullable=False, comment='Хеш ревизии файла')
    modified_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now(),
                         nullable=False, comment='Дата модификации файла')
    file_id = Column(UUID(as_uuid=True), ForeignKey('file.id', ondelete="CASCADE"),
                     nullable=False, comment='Связь с файлом')
