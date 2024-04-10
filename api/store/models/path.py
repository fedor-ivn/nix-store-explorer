from pydantic import BaseModel


class PathsDifference(BaseModel):
    absent_in_store_1: list[str]
    absent_in_store_2: list[str]
