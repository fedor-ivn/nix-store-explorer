import asyncio
import os

import pytest
from sqlalchemy import select

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from src.db.db import async_session_maker, create_db_and_tables, engine  # noqa: E402
from src.store.models.store import Store  # noqa: E402
from src.utils.repository import SQLAlchemyRepository  # noqa: E402


@pytest.fixture
def repository():
    asyncio.run(create_db_and_tables())
    repository = SQLAlchemyRepository()
    repository.model = Store

    yield repository

    asyncio.run(engine.dispose())


@pytest.mark.asyncio
async def test_add_one(repository):
    store_id = await repository.add_one({"id": 1, "name": "store", "owner_id": 2})
    assert store_id == 1

    async with async_session_maker() as session:
        stmt = select(Store).where(Store.id == 1)
        result = await session.execute(stmt)
        stored_store = result.scalar_one()

    assert stored_store.id == 1
    assert stored_store.name == "store"


@pytest.mark.asyncio
async def test_get_one(repository):
    await repository.add_one({"id": 1, "name": "store", "owner_id": 2})

    store = await repository.get_one({"id": 1})

    assert store[0].id == 1
    assert store[0].name == "store"
    assert store[0].owner_id == 2


@pytest.mark.asyncio
async def test_get_all(repository):
    await repository.add_one({"id": 1, "name": "store1", "owner_id": 2})
    await repository.add_one({"id": 2, "name": "store2", "owner_id": 2})

    entities = await repository.get_all({"owner_id": 2})

    assert len(entities) == 2
    assert entities[0][0].id == 1
    assert entities[0][0].name == "store1"
    assert entities[0][0].owner_id == 2
    assert entities[1][0].id == 2
    assert entities[1][0].name == "store2"
    assert entities[1][0].owner_id == 2


@pytest.mark.asyncio
async def test_delete(repository):
    await repository.add_one({"id": 1, "name": "store1", "owner_id": 2})

    entities = await repository.delete({"id": 1})

    assert entities is None

    async with async_session_maker() as session:
        stmt = select(Store).where(Store.id == 1)
        result = await session.execute(stmt)
        stored_store = result.scalar_one_or_none()

    assert stored_store is None
