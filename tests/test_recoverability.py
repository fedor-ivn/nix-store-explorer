import asyncio
import os
import sqlite3
import threading
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient

from src.logic.core import remove_store

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from src.app import app  # noqa: E402
from src.db.db import create_db_and_tables, engine  # noqa: E402


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

    asyncio.run(engine.dispose())

    remove_store(Path("stores/1/store"))


@pytest.mark.asyncio
async def test_recoverability(client_server):
    client, server = client_server

    client.post("/store/store")
    client.post("/store/store/package/hello")

    server.should_exit = True

    with sqlite3.connect("./stores/1/store/nix/var/nix/db/db.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM validpaths")

        rows = cursor.fetchall()

        for row in rows:
            path = "./stores/1/store" + row[1]
            assert os.path.exists(path)
