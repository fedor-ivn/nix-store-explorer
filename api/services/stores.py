from pathlib import Path

from fastapi import HTTPException

from auth.schemas import User
from store import logic
from store.models.store import Store
from utils.repository import AbstractRepository


class StoreService:
    def __init__(self, store_repository: AbstractRepository):
        self.stores_path = Path("stores/")
        self.store_repository = store_repository()  # type: ignore

    async def add_store(self, name: str, user: User):
        store_path = self.stores_path / f"{user.id}/{name}"

        try:
            logic.create_store(store_path)
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
