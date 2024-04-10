from pydantic import BaseModel


class PathsDifferenceRequest(BaseModel):
    store_1_id: int
    store_2_id: int


class PathsDifference(BaseModel):
    absent_in_store_1: list[str]
    absent_in_store_2: list[str]
