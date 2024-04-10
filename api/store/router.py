from fastapi import APIRouter, Body

from store.models.path import PathsDifference
from store.models.store import StoreRequest, Store
from store.models.closure import ClosuresDifference, ClosureSize, Closure
from store.models.package import PackageRequest, PackageMeta, Package, PackageChange, VersionUpdate

router = APIRouter(prefix="/store")


@router.post("", response_model=Store)
def create_store(store_request: StoreRequest = Body(...)):
    store = Store(id=1, name=store_request.name, owner_id=1)
    return store


@router.get("/{name}", response_model=Store)
def get_store(name: str):
    store = Store(id=1, name=name, owner_id=1)
    return store


@router.delete("/{name}", response_model=Store)
def delete_store(name: str):
    store = Store(id=1, name=name, owner_id=1)
    return store


@router.post("/{store_name}/package", response_model=Package)
def add_package(store_name: str, package_request: PackageRequest = Body(...)):
    package = Package(id=1, name=package_request.name, store_id=1, closure=Closure())
    return package


@router.delete("/{store_name}/package/{package_name}", response_model=Package)
def delete_package(store_name: str, package_name: str):
    package = Package(id=1, name=package_name, store_id=1, closure=Closure())
    return package


@router.get("/{store_name}/difference/{other_store_name}", response_model=PathsDifference)
def get_paths_difference(store_name: str, other_store_name: str):
    paths_difference = PathsDifference(difference=["/nix/store/1", "/nix/store/2"])
    return paths_difference


@router.get(
    "/{store_name}/package/{package_name}/closure-difference/{other_package_name}",
    response_model=ClosuresDifference)
def get_closures_difference(store_name: str, package_name: str, other_package_name: str):
    closures_difference = ClosuresDifference(difference=[
        PackageChange(
            package_name="python",
            version_update=VersionUpdate(old="3.11", new="3.12"),
            size_update="+1.4 MiB"
        ),
        PackageChange(
            package_name="node",
            version_update=VersionUpdate(old="v20.11", new="v20.12.1"),
            size_update="+14.1 MiB"
        ),
    ])
    return closures_difference


@router.get("/{store_name}/package/{package_name}/closure_size", response_model=ClosureSize)
def get_closure_size(store_name: str, package_name: str):
    closure_size = ClosureSize(size=5)
    return closure_size


@router.get("/{store_name}/package/{package_name}", response_model=PackageMeta)
def get_package_meta(store_name: str, package_name: str):
    return PackageMeta(present=True, closure_size=3)
