import pytest
from fastapi_users.db import SQLAlchemyUserDatabase
from auth.database import get_user_db


@pytest.mark.asyncio
async def test_get_user_db():
    async for db in get_user_db():
        assert isinstance(db, SQLAlchemyUserDatabase)
