from enum import Enum as NativeEnum

from fastapi import HTTPException
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import Base


class TodoState(str, NativeEnum):
    done = 'done'
    active = 'active'
    passive = 'passive'
    important = 'important'


class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=False)
    state = Column(Enum(TodoState, name="todo_state"), nullable=False, server_default=TodoState.passive)
    created_at = Column(Date, nullable=False, server_default='NOW()')

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        transaction = cls(**kwargs)
        session.add(transaction)
        try:
            await session.commit()
            await session.refresh(transaction)
        except IntegrityError as e:
            print(str(e))
            await session.rollback()
            return Exception(str(e))
        return transaction

    @classmethod
    async def get(cls, session: AsyncSession, id: int):
        transaction = None
        try:
            transaction = await session.get(cls, id)
        except NoResultFound:
            return transaction
        return transaction

    @classmethod
    async def delete(cls, session: AsyncSession, id: int) -> bool:
        try:
            transaction = await cls.get(session, id)
            if transaction is None:
                return False
            await session.delete(transaction)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        return True

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **kwargs):
        try:
            transaction = await cls.get(session, id)
            if transaction is None:
                raise HTTPException(status_code=404, detail="Todo not found!")
            for key in kwargs:
                setattr(transaction, key, kwargs[key])
            await session.commit()
            await session.refresh(transaction)
            return transaction
        except Exception as e:
            await session.rollback()
            raise e
