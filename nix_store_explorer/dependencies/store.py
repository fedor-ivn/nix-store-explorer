from ..repositories.stores import StoreRepository, PackageRepository
from ..services.stores import StoreService, PackageService


def store_service_dependency():
    return StoreService(StoreRepository)  # type: ignore


def package_service_dependency():
    return PackageService(PackageRepository)  # type: ignore
