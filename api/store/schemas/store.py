from pydantic import BaseModel


class Store(BaseModel):
    id: int
    name: str
    owner_id: int
    paths: list[str] = []
