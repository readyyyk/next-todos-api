from __future__ import annotations

import urllib.parse
from sqlalchemy import Column, Integer, String, Date, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from models.crud import CRUD


def default_image(context):
    return "https://api.dicebear.com/7.x/identicon/svg?seed="+urllib.parse.quote_plus(context.get_current_parameters()["username"])


class User(CRUD):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    registered = Column(Date, nullable=False, server_default=func.now())
    image = Column(String, nullable=False, default=default_image)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> User:
        kwargs["password"] = kwargs["password"].encode('utf-8')
        kwargs["password"] = bcrypt.hashpw(kwargs["password"], bcrypt.gensalt()).decode('utf-8')
        return await super().create(session, **kwargs)

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **kwargs) -> User:
        if "password" in kwargs.keys():
            kwargs["password"] = kwargs["password"].encode('utf-8')
            kwargs["password"] = bcrypt.hashpw(kwargs["password"], bcrypt.gensalt()).decode('utf-8')
        return await super().update(session, id, **kwargs)

    @classmethod
    async def login(cls, session: AsyncSession, username: str, password: str) -> User | None:
        try:
            user = (await session.execute(select(cls).where(
                cls.username == username
            ))).scalars().first()
            is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
            if is_valid:
                return user
            else:
                return None
        except NoResultFound:
            return None
