import os
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from src.store.models.store import Store

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from src.utils.repository import SQLAlchemyRepository  # noqa: E402
from src.db.db import create_db_and_tables, async_session_maker  # noqa: E402


@pytest.fixture
def client():
    asyncio.run(create_db_and_tables())
    yield TestClient()


@pytest.mark.asyncio
async def test_add_one():
    repository = SQLAlchemyRepository()
    entity = await repository.add_one({"name": "store"})
    assert entity.id == 1
    assert entity.name == "store"

    async with async_session_maker() as session:
        stmt = select(Store).where(Store.id == 1)
        result = await session.execute(stmt)
        stored_store = result.scalar_one()

    assert stored_store.id == 1
    assert stored_store.name == "store"


@pytest.mark.asyncio
async def test_get_one():
    repository = SQLAlchemyRepository()
    await repository.add_one({"name": "store"})

    entities = repository.get_one({"id": 1})

    assert entities.id == 1
    assert entities.name == "store"


@pytest.mark.asyncio
async def test_get_all():
    repository = SQLAlchemyRepository()
    await repository.add_one({"name": "store1"})
    await repository.add_one({"name": "store2"})

    entities = repository.get_all()

    assert len(entities) == 2
    assert entities[0].id == 1
    assert entities[0].name == "store1"
    assert entities[1].id == 2
    assert entities[1].name == "store2"


@pytest.mark.asyncio
async def test_delete():
    repository = SQLAlchemyRepository()
    await repository.add_one({"name": "store"})

    entities = repository.delete({"id": 1})

    assert entities is None

    async with async_session_maker() as session:
        stmt = select(Store).where(Store.id == 1)
        result = await session.execute(stmt)
        stored_store = result.scalar_one_or_none()

    assert stored_store is None
