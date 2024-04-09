from pydantic import BaseModel


class StoreRequest(BaseModel):
    name: str


class Store(BaseModel):
    id: int
    name: str
    owner_id: int
    paths: list[str] = []
