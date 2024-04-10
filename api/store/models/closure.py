from pydantic import BaseModel

from store.models.package import Package, PackageChange


class Closure(BaseModel):
    packages: list["Package"] = []


class ClosuresDifference(BaseModel):
    difference: list[PackageChange]


class ClosureSize(BaseModel):
    size: int
