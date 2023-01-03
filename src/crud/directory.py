import uuid

from sqlalchemy import outerjoin, select
from sqlalchemy.engine.row import Row
from sqlalchemy.sql import func

from crud.base import SqlalchemyCrud
from db.models.directory import Directory
from db.models.file import File
from schemas.directory import Directory as DirectorySchema
from schemas.user import UserStatus


class DirectoryCrud(SqlalchemyCrud):
    model: type[Directory] = Directory   # type: ignore
    schema = DirectorySchema

    async def get_status(self, user_id: uuid.UUID) -> UserStatus:
        query = select(
            self.model.user_id,
            self.model.id,
            self.model.name,
            func.sum(File.size).label("used"),
            func.count(File.id).label("files"),
        ).select_from(
            outerjoin(self.model, File)
        ).where(self.model.user_id == user_id).group_by(
            self.model.user_id,
            self.model.id,
            self.model.name,
        )

        async with self.ro_session() as session:
            result = await session.execute(query)
            objs = result.fetchall()
            return UserStatus(**self._data_preparation(objs, user_id))

    @staticmethod
    def _data_preparation(objs: list[Row], user_id: uuid.UUID) -> dict:
        """Метод приводит данные к виду требуемому в response схеме."""
        data = {
            "info": {
                "account_id": user_id,
            },
            "folders": []
        }

        if objs:
            data["info"].update({"home_folder_id": objs[0]["id"]})   # type: ignore

            for obj in objs:
                obj = dict(obj)
                used = obj.get("used", 0)
                if not used:
                    used = 0
                files = obj.get("files")
                data["folders"].append(   # type: ignore
                    {
                        obj["name"]:
                            {"used": used, "files": files}
                    }
                )

        return data
