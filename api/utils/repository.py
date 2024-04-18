from abc import ABC, abstractmethod

from sqlalchemy import insert, select

from db.db import async_session_maker


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, filter_by: dict):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(  # type: ignore
                self.model.id  # type: ignore
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar_one()

    async def get_all(self, filter_by: dict) -> list:
        async with async_session_maker() as session:
            stmt = select(self.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            result = [res[0].to_read_model() for res in result.all()]
            return result
