from pydantic import BaseModel

from store.models.package import Package, PackageChange


class Closure(BaseModel):
    packages: list["Package"] = []


class ClosuresDifference(BaseModel):
    difference: list[PackageChange]


class ClosuresDifferenceRequest(BaseModel):
    closure_1: Closure
    closure_2: Closure


class ClosureSize(BaseModel):
    size: int
