from fastapi.testclient import TestClient
import asyncio
import pytest
import os
import shutil

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

from app import app  # noqa: E402
from db.db import create_db_and_tables  # noqa: E402


@pytest.fixture
def client():
    asyncio.run(create_db_and_tables())

    client = TestClient(app)

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

    token = login_response.cookies["fastapiusersauth"]

    client = TestClient(app, cookies={"fastapiusersauth": token})

    yield client

    try:
        os.remove("./test.db")
    except FileNotFoundError:
        pass

    shutil.rmtree("stores", ignore_errors=True)


def test_create_store(client):
    response = client.post("/store/store", json={})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "store", "owner_id": 1, "paths": []}


def test_create_store_already_exists(client):
    client.post("/store/store", json={})

    response = client.post("/store/store", json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "This store already exists!"}


def test_get_all_stores(client):
    client.post("/store/store1", json={})

    client.post("/store/store2", json={})

    response = client.get("/store")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "store1", "owner_id": 1, "paths": []},
        {"id": 2, "name": "store2", "owner_id": 1, "paths": []},
    ]


def test_get_store(client):
    client.post("/store/store", json={})

    response = client.get("/store/store")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "store", "owner_id": 1, "paths": []}


def test_get_store_not_found(client):
    response = client.get("/store/store")

    assert response.status_code == 404
    assert response.json() == {"detail": "Store store was not found!"}


def test_delete_store(client):
    client.post("/store/store", json={})

    response = client.delete("/store/store")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "store", "owner_id": 1, "paths": []}

    response = client.get("/store/store")

    assert response.status_code == 404
    assert response.json() == {"detail": "Store store was not found!"}


def test_delete_store_not_found(client):
    response = client.delete("/store/store")

    assert response.status_code == 404
    assert response.json() == {"detail": "Store store was not found!"}


def test_add_package(client):
    client.post("/store/store", json={})

    response = client.post("/store/store/package/package", json={})

    assert response.status_code == 200
    print(response.json())
    assert response.json() == {
        "id": 1,
        "name": "package",
        "store_id": 1,
        "closure": {"packages": []},
    }


def test_delete_package(client):
    client.post("/store/store", json={})

    client.post("/store/store/package/package", json={})

    response = client.delete("/store/store/package/package")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "package",
        "store_id": 1,
        "closure": {"packages": []},
    }


def test_get_paths_difference(client):
    response = client.get("/store/store1/difference/store2")

    assert response.status_code == 200
    assert response.json() == {"absent_in_store_1": [], "absent_in_store_2": []}


def test_get_closures_difference(client):
    response = client.get(
        "/store/store1/package/package1/closure-difference/store2/package2"
    )

    assert response.status_code == 200
    assert response.json() == {"absent_in_closure_1": [], "absent_in_closure_2": []}


def test_get_package_meta():
    pass
