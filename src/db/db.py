import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db")
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)  # type: ignore
Base: DeclarativeMeta = declarative_base()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:  # type: ignore
        yield session
