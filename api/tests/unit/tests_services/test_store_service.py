import pytest
import shutil
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from auth.schemas import User
from store.models.store import Store
from store.schemas.store import Store as StoreSchema
from services.stores import StoreService


@pytest.fixture
def store_service():
    with patch(
        "services.stores.AbstractRepository", new_callable=AsyncMock
    ) as mock_repo:
        service = StoreService(mock_repo)
        yield service, mock_repo

    shutil.rmtree("stores/", ignore_errors=True)


def test_store_service_init(store_service):
    service, mock_repo = store_service
    assert isinstance(service.stores_path, Path)
    assert mock_repo.called


@pytest.mark.asyncio
async def test_add_store_already_exists(store_service):
    service, _ = store_service
    os.makedirs("stores/1/store")
    with pytest.raises(HTTPException):
        await service.add_store("store", User(id=1))


@pytest.mark.asyncio
async def test_add_store(store_service):
    service, _ = store_service
    service.store_repository = AsyncMock()
    service.store_repository.add_one.return_value = 1
    store = await service.add_store("store", User(id=1))
    assert store.id == 1
    assert store.name == "store"
    assert store.owner_id == 1


@pytest.mark.asyncio
async def test_get_stores(store_service):
    service, _ = store_service
    service.store_repository = AsyncMock()
    service.store_repository.get_all.return_value = [
        [Store(id=1, name="store", owner_id=1)]
    ]
    stores = await service.get_stores(User(id=1))
    assert stores == [StoreSchema(id=1, name="store", owner_id=1)]


@pytest.mark.asyncio
async def test_get_store_not_found(store_service):
    service, _ = store_service
    service.store_repository = AsyncMock()
    service.store_repository.get_one.return_value = None
    with pytest.raises(HTTPException):
        await service.get_store("store", User(id=1))


@pytest.mark.asyncio
async def test_get_store(store_service):
    service, _ = store_service
    service.store_repository = AsyncMock()
    service.store_repository.get_one.return_value = [
        Store(id=1, name="store", owner_id=1)
    ]
    store = await service.get_store("store", User(id=1))
    assert store == StoreSchema(id=1, name="store", owner_id=1)


@pytest.mark.asyncio
async def test_delete_store(store_service):
    service, _ = store_service
    service.store_repository = AsyncMock()
    service.get_store = AsyncMock()
    service.get_store.return_value = StoreSchema(id=1, name="store", owner_id=1)
    await service.add_store("store", User(id=1))
    store = await service.delete_store("store", User(id=1))
    assert store == StoreSchema(id=1, name="store", owner_id=1)
    assert not os.path.exists("stores/1/store")
