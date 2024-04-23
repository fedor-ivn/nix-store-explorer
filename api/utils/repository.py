from abc import ABC, abstractmethod
from typing import Sequence

from sqlalchemy import Row, insert, select
from sqlalchemy import delete as sqlalchemy_delete

from db.db import async_session_maker

class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, filter_by: dict) -> Sequence[Row]:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, filter_by: dict) -> Row | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, filter_by: dict):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with async_session_maker() as session:
            stmt = (
                insert(self.model)
                .values(**data)
                .returning(  # type: ignore
                    self.model.id  # type: ignore
                )
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def get_all(self, filter_by: dict) -> Sequence[Row]:
        async with async_session_maker() as session:
            stmt = select(self.model).filter_by(**filter_by)  # type: ignore
            result = await session.execute(stmt)
            return result.fetchall()

    async def get_one(self, filter_by: dict) -> Row | None:
        async with async_session_maker() as session:
            stmt = select(self.model).filter_by(**filter_by)  # type: ignore
            result = await session.execute(stmt)
            result = result.fetchone()
            return result

    async def delete(self, filter_by: dict):
        async with async_session_maker() as session:
            stmt = sqlalchemy_delete(self.model).filter_by(**filter_by)  # type: ignore
            await session.execute(stmt)
            await session.commit()
