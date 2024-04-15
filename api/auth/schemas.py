from fastapi_users import schemas
from pydantic.version import VERSION as PYDANTIC_VERSION


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass
