import asyncio
import os

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from src.app import app  # noqa: E402
from src.db.db import create_db_and_tables  # noqa: E402

EXAMPLE_USER = {
    "email": "user@example.com",
    "password": "string",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
}


REGISTER_RESPONSE = {
    "id": 1,
    "email": "user@example.com",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
}


LOGIN_DATA = {
    "username": "user@example.com",
    "password": "string",
}


@pytest.fixture
def client():
    asyncio.run(create_db_and_tables())
    yield TestClient(app)
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass


def test_register(client):
    response = client.post(
        "/auth/register",
        json=EXAMPLE_USER,
    )
    assert response.status_code == 201
    assert response.json() == REGISTER_RESPONSE


def test_login(client):
    client.post(
        "/auth/register",
        json=EXAMPLE_USER,
    )

    response = client.post(
        "/auth/jwt/login",
        data=LOGIN_DATA,
    )

    assert response.status_code == 204


def test_logout(client):
    client.post(
        "/auth/register",
        json=EXAMPLE_USER,
    )

    login_response = client.post(
        "/auth/jwt/login",
        data=LOGIN_DATA,
    )

    cookies = login_response.cookies["fastapiusersauth"]

    response = client.post(
        "/auth/jwt/logout",
        cookies={"fastapiusersauth": cookies},
    )

    assert response.status_code == 204
