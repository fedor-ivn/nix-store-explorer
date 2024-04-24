from repositories.stores import PackageRepository, StoreRepository
from services.stores import PackageService, StoreService


def store_service_dependency():
    return StoreService(StoreRepository)  # type: ignore


def package_service_dependency():
    return PackageService(PackageRepository)  # type: ignore
