from datetime import datetime

from pydantic import BaseModel, field_serializer


class UserSchemaBase(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    image: str


class UserSchema(UserSchemaBase):
    registered: datetime

    @field_serializer('registered')
    def serialize_dt(self, dt: datetime, _info):
        return dt.timestamp()

    class Config:
        from_attributes = True


class UserSchemaCreate(UserSchemaBase):
    id: None = None
    password: str
    image: str | None = None


class UserSchemaUpdate(UserSchemaBase):
    id: None = None
    username: None = None
    firstname: str | None = None
    lastname: str | None = None
    image: str | None = None
