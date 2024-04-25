import os
import asyncio
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from app import app  # noqa: E402
from db.db import create_db_and_tables  # noqa: E402

client = TestClient(app)


@pytest.fixture
def create_db():
    asyncio.run(create_db_and_tables())
    yield
    try:
        os.remove("./test.db")
    except FileNotFoundError:
        pass


def test_register(create_db):
    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "email": "user@example.com",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
    }


def test_login(create_db):
    client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )

    response = client.post(
        "/auth/jwt/login",
        data={
            "username": "user@example.com",
            "password": "string",
        },
    )

    assert response.status_code == 204


def test_logout(create_db):
    client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )

    login_response = client.post(
        "/auth/jwt/login",
        data={
            "username": "user@example.com",
            "password": "string",
        },
    )

    cookies = login_response.cookies["fastapiusersauth"]

    response = client.post(
        "/auth/jwt/logout",
        cookies={"fastapiusersauth": cookies},
    )

    assert response.status_code == 204
