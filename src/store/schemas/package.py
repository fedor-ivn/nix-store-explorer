from pydantic import BaseModel


class PackageMeta(BaseModel):
    present: bool
    closure_size: int


class Package(BaseModel):
    id: int
    name: str
    store_id: int
    closure: "Closure"


class VersionUpdate(BaseModel):
    old: str
    new: str


class PackageChange(BaseModel):
    package_name: str
    version_update: VersionUpdate
    size_update: str


class Closure(BaseModel):
    packages: list[str] = []


class ClosuresDifference(BaseModel):
    absent_in_package_1: list[str]
    absent_in_package_2: list[str]


class ClosureSize(BaseModel):
    size: int
