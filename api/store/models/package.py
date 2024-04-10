from pydantic import BaseModel


class PackageRequest(BaseModel):
    name: str
    store_id: int


class PackagePresenceRequest(BaseModel):
    store_name: str
    package_name: str


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
