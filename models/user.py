from datetime import datetime
import urllib.parse

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import Base


def default_image(context):
    return "https://api.dicebear.com/7.x/identicon/svg?seed="+urllib.parse.quote_plus(context.get_current_parameters()["username"])


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    registered = Column(Date, nullable=False, default=datetime.now())
    image = Column(String, nullable=False, default=default_image)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs):
        new_user = cls(**kwargs)
        session.add(new_user)
        try:
            await session.commit()
            await session.refresh(new_user)
        except IntegrityError as e:
            await session.rollback()
            return Exception(str(e))
        finally:
            return new_user

    @classmethod
    async def get(cls, session: AsyncSession, id: int):
        transaction = None
        try:
            transaction = await session.get(cls, id)
        except NoResultFound:
            return transaction
        finally:
            return transaction
