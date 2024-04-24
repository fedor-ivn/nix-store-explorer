from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.auth import fastapi_users
from src.auth.schemas import User
from src.dependencies.store import package_service_dependency, store_service_dependency
from src.services.stores import PackageService, StoreService
from src.store.schemas.package import (
    ClosuresDifference,
    Package,
    PackageMeta,
)
from src.store.schemas.path import PathsDifference
from src.store.schemas.store import Store

router = APIRouter(prefix="/store")
current_user = fastapi_users.current_user()


@router.post("/{name}", response_model=Store)
async def create_store(
    name: str,
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    user: User = Depends(current_user),
):
    store = await store_service.add_store(name, user)
    return store


@router.get("", response_model=list[Store])
async def get_all_stores(
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    user: User = Depends(current_user),
):
    stores = await store_service.get_stores(user)
    return stores


@router.get("/{name}", response_model=Store)
async def get_store(
    name: str,
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    user: User = Depends(current_user),
):
    stores = await store_service.get_store(name, user)
    return stores


@router.delete("/{name}", response_model=Store)
async def delete_store(
    name: str,
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    user: User = Depends(current_user),
):
    store = await store_service.delete_store(name, user)
    return store


@router.post("/{store_name}/package/{package_name}", response_model=Package)
async def add_package(
    store_name: str,
    package_name: str,
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    package_service: Annotated[PackageService, Depends(package_service_dependency)],
    user: User = Depends(current_user),
):
    package: Package = await store_service.add_package(
        store_name, package_name, user, package_service
    )
    return package


@router.delete("/{store_name}/package/{package_name}", response_model=Package)
async def delete_package(
    store_name: str,
    package_name: str,
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    package_service: Annotated[PackageService, Depends(package_service_dependency)],
    user: User = Depends(current_user),
):
    package: Package = await store_service.delete_package(
        store_name, package_name, user, package_service
    )
    return package


@router.get(
    "/{store_name}/difference/{other_store_name}", response_model=PathsDifference
)
async def get_paths_difference(
    store_name: str,
    other_store_name: str,
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    user: User = Depends(current_user),
):
    difference_1, difference_2 = await store_service.get_paths_difference(
        store_name, other_store_name, user
    )

    paths_difference = PathsDifference(
        absent_in_store_1=difference_2,
        absent_in_store_2=difference_1,
    )
    return paths_difference


@router.get(
    "/{store_name}/package/{package_name}/closure-difference/{other_store_name}/{other_package_name}",
    response_model=ClosuresDifference,
)
async def get_closures_difference(
    store_name: str,
    package_name: str,
    other_store_name: str,
    other_package_name: str,
    store_service: Annotated[StoreService, Depends(store_service_dependency)],
    user: User = Depends(current_user),
):
    """
    Closure difference for packages from the different stores
    """
    closures_difference = await store_service.get_closures_difference(
        store_name, package_name, other_store_name, other_package_name, user
    )
    return closures_difference


@router.get("/{store_name}/package/{package_name}", response_model=PackageMeta)
def get_package_meta(store_name: str, package_name: str):
    return PackageMeta(present=True, closure_size=3)
