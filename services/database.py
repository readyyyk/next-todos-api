import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (AsyncConnection,
                                    AsyncEngine,
                                    async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None

    def init(self, host: str):
        self._engine = create_async_engine(host)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception('Database manager closed before initialization!')
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception('Trying to connect before initialization!')

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception as e:
                await connection.rollback()
                raise e

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncConnection]:
        if self._sessionmaker is None:
            raise Exception('Trying to create session before initialization!')

        session = self._sessionmaker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager()


async def get_session():
    async with sessionmanager.session() as session:
        yield session
