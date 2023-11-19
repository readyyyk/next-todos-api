from datetime import datetime
from pydantic import BaseModel
from models.todo import TodoState
from views.schemas.user import UserSchema


class TodoSchema(BaseModel):
    id: int
    owner_id: int
    description: str
    state: TodoState
    created_at: datetime


class TodoSchemaCreate(TodoSchema):
    id: None = None
    state: None = None
    owner_id: None = None
    created_at: None = None


class TodoSchemaUpdate(TodoSchema):
    id: None = None
    owner_id: None = None
    created_at: None = None
    description: str | None = None
    state: TodoState | None = None


class TodoWithOwnerSchema(TodoSchema):
    owner: UserSchema

