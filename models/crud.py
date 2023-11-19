from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any


class CRUD:
    @classmethod
    async def create(cls: Any, session: AsyncSession, **kwargs):
        transaction = cls(**kwargs)
        session.add(transaction)
        try:
            await session.commit()
            await session.refresh(transaction)
        except IntegrityError as e:
            await session.rollback()
            raise Exception("IntegrityError on creating " + cls.__name__)
        return transaction

    @classmethod
    async def get(cls, session: AsyncSession, id: int):
        try:
            transaction = await session.get(cls, id)
            return transaction
        except NoResultFound:
            return None

    async def delete_inst(self, session: AsyncSession) -> bool:
        try:
            if self is None:
                return False
            await session.delete(self)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        return True

    @classmethod
    async def delete(cls, session: AsyncSession, id: int) -> bool:
        transaction = await cls.get(session, id)
        return await transaction.delete_inst(session)

    async def update_inst(self, session: AsyncSession, **kwargs):
        try:
            if self is None:
                raise HTTPException(status_code=404, detail=self.__name__+" not found!")
            for key in kwargs:
                setattr(self, key, kwargs[key])
            await session.commit()
            await session.refresh(self)
            return self
        except Exception as e:
            await session.rollback()
            raise e

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **kwargs):
        transaction = await cls.get(session, id)
        updated = await cls.update_inst(transaction, session, **kwargs)
        return updated
