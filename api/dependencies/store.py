from repositories.stores import StoreRepository
from services.stores import StoreService


def store_service_dependency():
    return StoreService(StoreRepository)
