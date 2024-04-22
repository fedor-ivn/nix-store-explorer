from repositories.stores import StoreRepository
from store.models.store import Store


def test_store_repository():
    assert StoreRepository.model == Store
