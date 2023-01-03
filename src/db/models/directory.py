import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from db.base import Base


class Directory(Base):
    __tablename__ = 'directory'
    __table_args__ = (
        UniqueConstraint('name', 'user_id', name='uix_name_user_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, nullable=False)
    name = Column(String(100), nullable=False, index=True, comment='Имя директории')
    created_ad = Column(DateTime(timezone=True), default=func.now(), nullable=False, comment='Дата создания')
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete="CASCADE"),
                     nullable=False, comment='Связь с пользователем')
    parent_id = Column(UUID(as_uuid=True), ForeignKey('directory.id', ondelete="CASCADE"),
                       comment='Может быть родительская директория')
