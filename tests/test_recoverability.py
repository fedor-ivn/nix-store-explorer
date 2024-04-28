import asyncio
import os
import shutil
import threading
from contextlib import suppress

import pytest
import uvicorn
from fastapi.testclient import TestClient
from sqlalchemy import select

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from src.app import app  # noqa: E402
from src.db.db import async_session_maker, create_db_and_tables  # noqa: E402
from src.store.models.store import Store  # noqa: E402


@pytest.fixture
def client_server():
    asyncio.run(create_db_and_tables())
    config = uvicorn.Config(app=app, host="localhost", port=8000)
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run)
    thread.start()

    client = TestClient(app)

    new_user = {
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }

    login_data = {
        "username": "user@example.com",
        "password": "string",
    }

    client.post(
        "/auth/register",
        json=new_user,
    )

    login_response = client.post(
        "/auth/jwt/login",
        data=login_data,
    )

    token = login_response.cookies["fastapiusersauth"]

    client = TestClient(app, cookies={"fastapiusersauth": token})

    yield client, server

    server.should_exit = True
    thread.join()

    # Suppressing the error
    with suppress(Exception):
        server.shutdown()

    os.remove("test.db")
    shutil.rmtree("stores", ignore_errors=True)


@pytest.mark.asyncio
async def test_recoverability(client_server):
    client, server = client_server

    for i in range(1, 10):
        client.post(f"/store/store_{i}")

    server.should_exit = True

    stores_paths = os.listdir("stores/1")

    async with async_session_maker() as session:
        stmt = select(Store).where(Store.owner_id == 1)
        result = await session.execute(stmt)

    stores_database = [store[0].name for store in result.all()]

    print(stores_paths)
    print(stores_database)

    assert set(stores_paths) == set(stores_database)
