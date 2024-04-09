from pydantic import BaseModel


class PathsDifferenceRequest(BaseModel):
    store_1_id: int
    store_2_id: int


class PathsDifference(BaseModel):
    difference: list[str]
