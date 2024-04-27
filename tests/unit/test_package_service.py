import os
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
from fastapi import HTTPException

from src.auth.schemas import User
from src.logic.exceptions import (
    AttributeNotProvidedException,
    BrokenPackageException,
    InsecurePackageException,
    NotAvailableOnHostPlatformException,
    PackageNotInstalledException,
    StillAliveException,
    UnfreeLicenceException,
)
from src.store.models.package import Package
from src.services.stores import PackageService
from src.store.models.store import Store
from src.store.schemas.package import Package as PackageSchema
from src.store.schemas.store import Store as StoreSchema
from src.store.schemas.package import ClosuresDifference, PackageMeta, Closure


@pytest.fixture
def package_service():
    with patch(
        "src.services.stores.AbstractRepository", new_callable=MagicMock
    ) as mock_repo:
        service = PackageService(mock_repo)
        yield service


@pytest.mark.asyncio
async def test_add_package(package_service):
    service = package_service

    with patch("src.services.stores.core_logic.install_package") as mock_install:
        mock_install.return_value = None

        service.repository.add_one = AsyncMock()
        service.repository.add_one.return_value = 1

        package_id = await service.add_package(Path("store"), "package", 1)

        assert package_id == 1
        service.repository.add_one.assert_called_once_with({"name": "package", "store_id": 1})
        mock_install.assert_called_once_with(Path("store"), "package")


@pytest.mark.asyncio
async def test_add_package_insecure(package_service):
    service = package_service

    with patch("src.services.stores.core_logic.install_package") as mock_install:
        mock_install.side_effect = InsecurePackageException
        with pytest.raises(HTTPException) as exc:
            await service.add_package(Path("store"), "package", 1)

            assert exc.value.status_code == 400
            assert exc.value.detail == "Package package is marked as insecure!"


@pytest.mark.asyncio
async def test_add_package_broken(package_service):
    service = package_service

    with patch("src.services.stores.core_logic.install_package") as mock_install:
        mock_install.side_effect = BrokenPackageException
        with pytest.raises(HTTPException) as exc:
            await service.add_package(Path("store"), "package", 1)

            assert exc.value.status_code == 400
            assert exc.value.detail == "Package package is marked as broken!"


@pytest.mark.asyncio
async def test_add_package_not_available_on_host_platform(package_service):
    service = package_service

    with patch("src.services.stores.core_logic.install_package") as mock_install:
        mock_install.side_effect = NotAvailableOnHostPlatformException
        with pytest.raises(HTTPException) as exc:
            await service.add_package(Path("store"), "package", 1)

            assert exc.value.status_code == 400
            assert exc.value.detail == "Package package is not available on your host platform!"


@pytest.mark.asyncio
async def test_add_package_attribute_not_provided(package_service):
    service = package_service

    with patch("src.services.stores.core_logic.install_package") as mock_install:
        mock_install.side_effect = AttributeNotProvidedException
        with pytest.raises(HTTPException) as exc:
            await service.add_package(Path("store"), "package", 1)

            assert exc.value.status_code == 400
            assert exc.value.detail == "Your flake does not provide this attribute!"


@pytest.mark.asyncio
async def test_add_package_unfree_license(package_service):
    service = package_service

    with patch("src.services.stores.core_logic.install_package") as mock_install:
        mock_install.side_effect = UnfreeLicenceException
        with pytest.raises(HTTPException) as exc:
            await service.add_package(Path("store"), "package", 1)

            assert exc.value.status_code == 400
            assert exc.value.detail == "Package package has an unfree license!"


@pytest.mark.asyncio
async def test_add_package_unexpected_error(package_service):
    service = package_service

    with patch("src.services.stores.core_logic.install_package") as mock_install:
        mock_install.side_effect = Exception
        with pytest.raises(HTTPException) as exc:
            await service.add_package(Path("store"), "package", 1)

            assert exc.value.status_code == 500
            assert exc.value.detail == "Unexpected error"


@pytest.mark.asyncio
async def test_get_package_none(package_service):
    service = package_service

    service.repository.get_one = AsyncMock()
    service.repository.get_one.return_value = None

    package = await service.get_package("package", 1)

    assert package == None
    service.repository.get_one.assert_called_once_with({"name": "package", "store_id": 1})


@pytest.mark.asyncio
async def test_get_package(package_service):
    service = package_service

    service.repository.get_one = AsyncMock()
    service.repository.get_one.return_value = [Package(id=1, name="package", store_id=1)]

    package = await service.get_package("package", 1)

    assert package.id == 1
    assert package.name == "package"
    assert package.store_id == 1

    service.repository.get_one.assert_called_once_with({"name": "package", "store_id": 1})


@pytest.mark.asyncio
async def test_delete_package_none(package_service):
    service = package_service

    service.repository.get_one = AsyncMock()
    service.repository.get_one.return_value = None

    package = await service.delete_package("package", 1)

    assert package == None
    service.repository.get_one.assert_called_once_with({"name": "package", "store_id": 1})


@pytest.mark.asyncio
async def test_delete_package(package_service):
    service = package_service

    service.repository.get_one = AsyncMock()
    service.repository.get_one.return_value = [Package(id=1, name="package", store_id=1)]

    service.repository.delete = AsyncMock()

    package = await service.delete_package("package", 1)

    assert package.id == 1
    assert package.name == "package"
    assert package.store_id == 1

    service.repository.get_one.assert_called_once_with({"name": "package", "store_id": 1})
    service.repository.delete.assert_called_once_with({"name": "package", "store_id": 1})
