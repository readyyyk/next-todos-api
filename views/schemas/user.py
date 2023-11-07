from datetime import datetime

from pydantic import BaseModel, field_serializer


class UserSchemaBase(BaseModel):
    username: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    image: str | None = None


class UserSchema(UserSchemaBase):
    id: int
    registered: datetime | None = None

    @field_serializer('registered')
    def serialize_dt(self, dt: datetime, _info):
        return dt.timestamp()

    class Config:
        from_attributes = True


class UserSchemaCreate(UserSchemaBase):
    password: str | None = None
