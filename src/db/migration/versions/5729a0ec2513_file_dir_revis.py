"""file_dir_revis

Revision ID: 5729a0ec2513
Revises: 47a6a801b9ea
Create Date: 2022-12-30 14:06:02.278357

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5729a0ec2513'
down_revision = '47a6a801b9ea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('directory',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False, comment='Имя директории'),
    sa.Column('created_ad', sa.DateTime(timezone=True), nullable=False, comment='Дата создания'),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Связь с пользователем'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'user_id', name='uix_name_user_id')
    )
    op.create_index(op.f('ix_directory_id'), 'directory', ['id'], unique=False)
    op.create_index(op.f('ix_directory_name'), 'directory', ['name'], unique=False)
    op.create_table('file',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False, comment='Имя файла'),
    sa.Column('path', sa.String(length=500), nullable=False, comment='Путь до файла'),
    sa.Column('size', sa.Integer(), nullable=False, comment='Размер файла'),
    sa.Column('created_ad', sa.DateTime(timezone=True), nullable=False, comment='Дата добавления файла'),
    sa.Column('directory_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Связь с директорией'),
    sa.ForeignKeyConstraint(['directory_id'], ['directory.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'directory_id', name='uix_name_directory_id'),
    sa.UniqueConstraint('path')
    )
    op.create_index(op.f('ix_file_id'), 'file', ['id'], unique=False)
    op.create_index(op.f('ix_file_name'), 'file', ['name'], unique=False)
    op.create_table('revision',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('hash', sa.String(length=500), nullable=False, comment='Хеш ревизии файла'),
    sa.Column('modified_at', sa.DateTime(timezone=True), nullable=False, comment='Дата модификации файла'),
    sa.Column('file_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Связь с файлом'),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hash', 'file_id', name='uix_hash_file_id')
    )
    op.create_index(op.f('ix_revision_id'), 'revision', ['id'], unique=False)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_revision_id'), table_name='revision')
    op.drop_table('revision')
    op.drop_index(op.f('ix_file_name'), table_name='file')
    op.drop_index(op.f('ix_file_id'), table_name='file')
    op.drop_table('file')
    op.drop_index(op.f('ix_directory_name'), table_name='directory')
    op.drop_index(op.f('ix_directory_id'), table_name='directory')
    op.drop_table('directory')
    # ### end Alembic commands ###