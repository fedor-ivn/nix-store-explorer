from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import Row

from auth.schemas import User
from logic import core as core_logic
from logic.exceptions import (
    InsecurePackageException,
    BrokenPackageException,
    NotAvailableOnHostPlatformException,
    AttributeNotProvidedException,
    UnfreeLicenceException
)
from store.models.store import Store
from store.models.package import Package
from store.schemas.package import Package as PackageSchema, Closure
from utils.repository import AbstractRepository


class PackageService:
    def __init__(self, repository: AbstractRepository):
        self.repository = repository()  # type: ignore

    async def add_package(self, store_path: Path, package_name: str, store_id: int) -> int:
        try:
            core_logic.install_package(store_path, package_name)
        except InsecurePackageException:
            raise HTTPException(
                status_code=400,
                detail=f"Package {package_name} is marked as insecure!"
            )
        except BrokenPackageException:
            raise HTTPException(
                status_code=400,
                detail=f"Package {package_name} is marked as broken!"
            )
        except NotAvailableOnHostPlatformException:
            raise HTTPException(
                status_code=400,
                detail=f"Package {package_name} is not available on your host platform!"
            )
        except AttributeNotProvidedException:
            raise HTTPException(
                status_code=400,
                detail="Your flake does not provide this attribute!"
            )
        except UnfreeLicenceException:
            raise HTTPException(
                status_code=400,
                detail=f"Package {package_name} has an unfree license!"
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Unexpected error"
            )

        package = {
            "name": package_name,
            "store_id": store_id
        }
        package_id = await self.repository.add_one(package)
        return package_id

    async def get_package(self, package_name: str, store_id: int) -> PackageSchema | None:
        filter_by = {
            "name": package_name,
            "store_id": store_id
        }
        package_row: Row[Package] = await self.repository.get_one(filter_by)
        if package_row is None:
            return None

        package: Package = package_row[0]
        package_schema: PackageSchema = package.to_read_model()

        return package_schema


class StoreService:
    def __init__(self, store_repository: AbstractRepository):
        self.stores_path = Path("../stores")
        self.store_repository = store_repository()  # type: ignore

    async def add_store(self, name: str, user: User):
        store_path = self.stores_path / str(user.id) / name

        try:
            core_logic.create_store(store_path)
        except FileExistsError:
            raise HTTPException(400, "This store already exists!")

        store_dict = {
            "name": name,
            "owner_id": user.id
        }
        store_id = await self.store_repository.add_one(data=store_dict)

        return Store(id=store_id, name=name, owner_id=user.id)

    async def get_stores(self, user: User):
        filter_by = {
            "owner_id": user.id
        }
        stores = await self.store_repository.get_all(filter_by)
        result = [store[0].to_read_model() for store in stores]
        return result

    async def get_store(self, name: str, user: User):
        filter_by = {
            "owner_id": user.id,
            "name": name,
        }

        store = await self.store_repository.get_one(filter_by)

        if store is None:
            raise HTTPException(status_code=404, detail=f'Store {name} was not found!')

        result = store[0].to_read_model()
        return result

    async def delete_store(self, name: str, user: User):
        filter_by = {
            "owner_id": user.id,
            "name": name,
        }
        store = await self.get_store(name, user)
        await self.store_repository.delete(filter_by)

        store_path = self.stores_path / str(user.id) / name
        core_logic.remove_store(store_path)

        return store

    async def add_package(
            self,
            store_name: str,
            package_name: str,
            user: User,
            package_service: PackageService
    ) -> PackageSchema:
        store_path = self.stores_path / str(user.id) / store_name

        store = await self.get_store(store_name, user)
        package: PackageSchema | None = await package_service.get_package(package_name, store.id)

        if package is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Package {package_name} is already added to the store {store_name}"
            )

        package_id: int = await package_service.add_package(store_path, package_name, store.id)
        raw_closure: list[str] = core_logic.get_closure(store_path, package_name)

        package = PackageSchema(id=package_id, name=package_name, store_id=store.id, closure=Closure(packages=raw_closure))
        return package
