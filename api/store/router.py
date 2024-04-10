from fastapi import APIRouter, Body

from auth.models.user import User
from store.models.path import PathsDifference
from store.models.store import StoreRequest, Store
from store.models.closure import ClosuresDifference, ClosureSize, Closure
from store.models.package import PackageRequest, PackagePresence, Package

router = APIRouter(prefix="/store")


@router.post("", response_model=Store)
def create_store(store_request: StoreRequest = Body(...)):
    store = Store(id=1, name=store_request.name, owner_id=1)
    return store


@router.delete("/{name}", response_model=Store)
def delete_store(name: str):
    store = Store(id=1, name=name, owner_id=1)
    return store


@router.get("/owner/{store_id}", response_model=User)
def get_owner(store_id: int):
    return User(id=1)


@router.post("/{name}/package", response_model=Package)
def add_package(store_name: str, package_request: PackageRequest = Body(...)):
    package = Package(id=1, name=package_request.name, store_id=1, closure=Closure())
    return package


@router.delete("/{name}/package", response_model=Package)
def delete_package(store_name: str, package_request: PackageRequest = Body(...)):
    package = Package(id=1, name=package_request.name, store_id=1, closure=Closure())
    return package


@router.get("/paths_difference", response_model=PathsDifference)
def get_paths_difference(store_1_id: int, store_2_id: int):
    paths_difference = PathsDifference(difference=["/nix/store/1", "/nix/store/2"])
    return paths_difference


@router.get("/closures_difference", response_model=ClosuresDifference)
def get_closures_difference(package_1_id: int, package_2_id: int):
    closures_difference = ClosuresDifference(difference=[
        Package(
            id=1,
            name="python",
            store_id=1,
            closure=Closure()
        ),
        Package(
            id=2,
            name="nodejs",
            store_id=2,
            closure=Closure()
        )
    ])
    return closures_difference


@router.get("/closure_size", response_model=ClosureSize)
def get_closure_size(package_id: int):
    closure_size = ClosureSize(size=5)
    return closure_size


@router.get("/package_presence", response_model=PackagePresence)
def get_package_presence(store_id: int, package_id: int):
    return PackagePresence(present=True)
