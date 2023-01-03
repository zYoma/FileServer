from crud.base import SqlalchemyCrud
from db.models.user import User
from schemas.user import User as UserSchema


class UserCrud(SqlalchemyCrud):
    model = User
    schema = UserSchema
