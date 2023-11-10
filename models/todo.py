from enum import Enum as NativeEnum
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.crud import CRUD


class TodoState(str, NativeEnum):
    done = 'done'
    active = 'active'
    passive = 'passive'
    important = 'important'


class Todo(CRUD):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=False)
    state = Column(Enum(TodoState, name="todo_state"), nullable=False, server_default=TodoState.passive)
    created_at = Column(Date, nullable=False, server_default='NOW()')

    @classmethod
    async def get_by_owner(cls, session: AsyncSession, owner_id: int):
        transaction = None
        try:
            transaction = (await session.execute(select(cls).where(cls.owner_id == owner_id))).scalars()
        except NoResultFound:
            return transaction
        return transaction
