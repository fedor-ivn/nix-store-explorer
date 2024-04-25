import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from bcrypt import checkpw

from auth.schemas import User

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from app import app  # noqa: E402
from db.db import async_session_maker, create_db_and_tables  # noqa: E402


@pytest.fixture
def client():
    asyncio.run(create_db_and_tables())
    yield TestClient(app)
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass



@pytest.mark.asyncio
async def test_password_security(client):
    new_user = {
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }

    client.post("/auth/register", json=new_user)

    async with async_session_maker() as session:
        stmt = select(User).where(User.email == new_user["email"])
        result = await session.execute(stmt)
        stored_user = result.scalar_one()

    assert stored_user.hashed_password != new_user["password"]
    assert checkpw(new_user["password"].encode(), stored_user.hashed_password.encode())
