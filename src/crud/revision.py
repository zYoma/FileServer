import uuid

from sqlalchemy import join, select

from crud.base import SqlalchemyCrud
from db.models.file import File
from db.models.revision import Revision
from schemas.revision import Revision as RevisionSchema
from schemas.revision import RevisionResponse
from utils.functools import is_valid_uuid


class RevisionCrud(SqlalchemyCrud):
    model: type[Revision] = Revision   # type: ignore
    schema = RevisionSchema

    async def get_revision(self, path: str, user_id: uuid.UUID, limit: int) -> list[RevisionResponse]:
        query = select(
            File.id,
            File.name,
            File.path,
            File.created_ad,
            self.model.id.label("rev_id"),
            self.model.hash,
            self.model.modified_at
        ).select_from(
            join(self.model, File)
        ).where(File.user_id == user_id)

        if is_valid_uuid(path):
            query = query.where(File.id == path)
        else:
            query = query.where(File.path == path)

        if limit:
            query = query.limit(limit)

        async with self.ro_session() as session:
            result = await session.execute(query)
            objs = result.fetchall()
            return [RevisionResponse(**x) for x in objs]
