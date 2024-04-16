from pathlib import Path

from fastapi import HTTPException

from auth.schemas import User
from store import logic
from utils.repository import AbstractRepository


class StoreService:
    def __init__(self, store_repository: AbstractRepository):
        self.stores_path = Path("stores/")
        self.store_repository = store_repository()

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
        store = await self.store_repository.add_one(data=store_dict)

        return store
