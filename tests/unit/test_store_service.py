import os
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.auth.schemas import User
from src.logic.exceptions import (
    StillAliveException,
)
from src.services.stores import StoreService
from src.store.models.store import Store
from src.store.schemas.package import Package as PackageSchema
from src.store.schemas.store import Store as StoreSchema


@pytest.fixture
def store_service():
    with patch(
        "src.services.stores.AbstractRepository", new_callable=MagicMock
    ) as mock_repo:
        service = StoreService(mock_repo)
        yield service

    shutil.rmtree("stores/", ignore_errors=True)


def test_store_service_init(store_service):
    service = store_service
    assert isinstance(service.stores_path, Path)


@pytest.mark.asyncio
async def test_add_store_already_exists(store_service):
    service = store_service
    os.makedirs("stores/1/store")
    with pytest.raises(HTTPException):
        await service.add_store("store", User(id=1))


@pytest.mark.asyncio
async def test_add_store(store_service):
    service = store_service
    service.store_repository = AsyncMock()
    service.store_repository.add_one.return_value = 1
    store = await service.add_store("store", User(id=1))
    assert store.id == 1
    assert store.name == "store"
    assert store.owner_id == 1
    assert os.path.exists("stores/1/store")


@pytest.mark.asyncio
async def test_get_stores(store_service):
    service = store_service
    service.store_repository = AsyncMock()
    service.store_repository.get_all.return_value = [
        [Store(id=1, name="store", owner_id=1)]
    ]
    stores = await service.get_stores(User(id=1))
    assert stores == [StoreSchema(id=1, name="store", owner_id=1)]


@pytest.mark.asyncio
async def test_get_store_not_found(store_service):
    service = store_service
    service.store_repository = AsyncMock()
    service.store_repository.get_one.return_value = None
    with pytest.raises(HTTPException):
        await service.get_store("store", User(id=1))


@pytest.mark.asyncio
async def test_get_store(store_service):
    service = store_service
    service.store_repository = MagicMock()
    service.store_repository.get_one = AsyncMock()
    service.store_repository.get_one.return_value = [
        Store(id=1, name="store", owner_id=1)
    ]
    store = await service.get_store("store", User(id=1))
    assert store == StoreSchema(id=1, name="store", owner_id=1)


@pytest.mark.asyncio
async def test_delete_store(store_service):
    service = store_service
    service.store_repository = AsyncMock()
    service.get_store = AsyncMock()
    service.get_store.return_value = StoreSchema(id=1, name="store", owner_id=1)
    await service.add_store("store", User(id=1))
    store = await service.delete_store("store", User(id=1))
    assert store == StoreSchema(id=1, name="store", owner_id=1)
    assert not os.path.exists("stores/1/store")


@pytest.mark.asyncio
async def test_add_package_already_added(store_service):
    service = store_service

    service.get_store = AsyncMock()
    service.get_store.return_value = StoreSchema(id=1, name="store", owner_id=1)

    service.package_service = AsyncMock()
    service.package_service.get_package.return_value = PackageSchema(
        id=1, name="package", store_id=1, closure={"packages": []}
    )

    with pytest.raises(HTTPException):
        await service.add_package("store", "package", User(id=1), service.package_service)


@pytest.mark.asyncio
async def test_add_package(store_service):
    service = store_service

    service.get_store = AsyncMock()
    service.get_store.return_value = StoreSchema(id=1, name="store", owner_id=1)

    service.package_service = AsyncMock()
    service.package_service.get_package.return_value = None

    service.package_service.add_package = AsyncMock()
    service.package_service.add_package.return_value = 1

    with patch("src.services.stores.core_logic.get_closure") as mock_closure:
        mock_closure.return_value = ["package"]

        package = await service.add_package("store", "package", User(id=1), service.package_service)
        assert package == PackageSchema(id=1, name="package", store_id=1, closure={"packages": ["package"]})
    

@pytest.mark.asyncio
async def test_delete_package(store_service):
    service = store_service

    service.get_store = AsyncMock()
    service.get_store.return_value = StoreSchema(id=1, name="store", owner_id=1)

    service.package_service = AsyncMock()
    service.package_service.delete_package = AsyncMock()
    service.package_service.delete_package.return_value = PackageSchema(
        id=1, name="package", store_id=1, closure={"packages": []}
    )

    with patch("src.services.stores.core_logic.remove_package") as mock_remove_package:
        package = await service.delete_package("store", "package", User(id=1), service.package_service)
        assert package == PackageSchema(id=1, name="package", store_id=1, closure={"packages": []})


@pytest.mark.asyncio
async def test_delete_package_exception(store_service):
    service = store_service

    service.get_store = AsyncMock()
    service.get_store.return_value = StoreSchema(id=1, name="store", owner_id=1)

    service.package_service = AsyncMock()
    service.package_service.delete_package = AsyncMock()
    service.package_service.delete_package.return_value = PackageSchema(
        id=1, name="package", store_id=1, closure={"packages": []}
    )

    with patch("src.services.stores.core_logic.remove_package") as mock_remove_package:
        mock_remove_package.side_effect = StillAliveException

        with pytest.raises(HTTPException):
            await service.delete_package("store", "package", User(id=1), service.package_service)


