import os
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from fastapi import HTTPException

from src.auth.schemas import User
from src.logic.exceptions import PackageNotInstalledException, StillAliveException
from src.services.stores import StoreService
from src.store.models.store import Store
from src.store.schemas.package import ClosuresDifference, PackageMeta
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
        await service.add_package(
            "store", "package", User(id=1), service.package_service
        )


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

        package = await service.add_package(
            "store", "package", User(id=1), service.package_service
        )
        assert package == PackageSchema(
            id=1, name="package", store_id=1, closure={"packages": ["package"]}
        )


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
        mock_remove_package.return_value = {"packages": []}
        package = await service.delete_package(
            "store", "package", User(id=1), service.package_service
        )
        assert package == PackageSchema(
            id=1, name="package", store_id=1, closure={"packages": []}
        )


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
            await service.delete_package(
                "store", "package", User(id=1), service.package_service
            )


@pytest.mark.asyncio
async def test_get_paths_difference(store_service):
    service = store_service

    with patch("src.services.stores.core_logic.get_paths") as mock_get_paths:
        mock_get_paths.side_effect = [{"path1", "path2"}, {"path3", "path2"}]

        store_1 = "store1"
        store_2 = "store2"
        user = User(id=1)

        paths_diff_1, paths_diff_2 = await service.get_paths_difference(
            store_1, store_2, user
        )

        calls = [
            call(service.stores_path / "1" / store_1),
            call(service.stores_path / "1" / store_2),
        ]

        assert mock_get_paths.call_args_list == calls
        assert paths_diff_1 == ["path1"]
        assert paths_diff_2 == ["path3"]


@pytest.mark.asyncio
async def test_closures_difference(store_service):
    service = store_service

    with patch("src.services.stores.core_logic.get_closure") as mock_get_closure:
        mock_get_closure.side_effect = [
            ["package1", "package2"],
            ["package2", "package3"],
        ]

        store_name = "store1"
        package_name = "package1"
        other_store_name = "store2"
        other_package_name = "package2"
        user = User(id=1)

        diff = await service.get_closures_difference(
            store_name, package_name, other_store_name, other_package_name, user
        )

        calls = [
            call(service.stores_path / "1" / store_name, package_name),
            call(service.stores_path / "1" / other_store_name, other_package_name),
        ]

        assert mock_get_closure.call_args_list == calls

        assert diff == ClosuresDifference(
            absent_in_package_1=["package3"], absent_in_package_2=["package1"]
        )


@pytest.mark.asyncio
async def test_get_packages_meta(store_service):
    service = store_service

    with patch(
        "src.services.stores.core_logic.get_closure_size"
    ) as mock_get_closure_size:
        mock_get_closure_size.return_value = 10

        store_name = "store"
        package_name = "package"
        user = User(id=1)

        meta = await service.get_package_meta(store_name, package_name, user)

        mock_get_closure_size.assert_called_once_with(
            service.stores_path / "1" / store_name, package_name
        )

        assert meta == PackageMeta(present=True, closure_size=10)


@pytest.mark.asyncio
async def test_get_packages_meta_not_exception(store_service):
    service = store_service

    with patch(
        "src.services.stores.core_logic.get_closure_size"
    ) as mock_get_closure_size:
        mock_get_closure_size.side_effect = PackageNotInstalledException

        store_name = "store"
        package_name = "package"
        user = User(id=1)

        meta = await service.get_package_meta(store_name, package_name, user)

        mock_get_closure_size.assert_called_once_with(
            service.stores_path / "1" / store_name, package_name
        )

        assert meta == PackageMeta(present=False, closure_size=0)
