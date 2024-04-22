from unittest.mock import patch
from dependencies.store import store_service_dependency
from repositories.stores import StoreRepository


def test_store_service_dependency():
    with patch("dependencies.store.StoreService") as mock_StoreService:
        store_service_dependency()
        mock_StoreService.assert_called_once_with(StoreRepository)
