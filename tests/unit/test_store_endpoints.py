import asyncio
import os
import shutil
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.store.schemas.package import (
    ClosuresDifference,
    Package,
    PackageMeta,
)

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from src.app import app  # noqa: E402
from src.db.db import create_db_and_tables, engine  # noqa: E402


@pytest.fixture
def client():
    asyncio.run(create_db_and_tables())

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

    yield client

    asyncio.run(engine.dispose())

    shutil.rmtree("stores", ignore_errors=True)


def test_create_store(client):
    response = client.post("/store/store")
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
    with patch("src.store.router.StoreService.add_package") as mock_add_package:
        mock_add_package.return_value = Package(
            id=1,
            name="package",
            store_id=1,
            closure={"packages": []},
        )

        response = client.post("/store/store/package/package", json={})

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "package",
            "store_id": 1,
            "closure": {"packages": []},
        }


def test_delete_package(client):
    with patch("src.store.router.StoreService.delete_package") as mock_delete_package:
        mock_delete_package.return_value = Package(
            id=1,
            name="package",
            store_id=1,
            closure={"packages": []},
        )

        response = client.delete("/store/store/package/package")

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "name": "package",
            "store_id": 1,
            "closure": {"packages": []},
        }


def test_get_paths_difference(client):
    with patch(
        "src.store.router.StoreService.get_paths_difference"
    ) as mock_get_paths_difference:
        mock_get_paths_difference.return_value = (
            ["store1"],
            ["store2"],
        )

        response = client.get("/store/store1/difference/store2")

        assert response.status_code == 200
        assert response.json() == {
            "absent_in_store_1": ["store2"],
            "absent_in_store_2": ["store1"],
        }


def test_get_closures_difference(client):
    with patch(
        "src.store.router.StoreService.get_closures_difference"
    ) as mock_get_closures_difference:
        mock_get_closures_difference.return_value = ClosuresDifference(
            absent_in_package_1=["package2"],
            absent_in_package_2=["package1"],
        )

        response = client.get(
            "/store/store/package/package/closure-difference/store/package"
        )

        assert response.status_code == 200
        assert response.json() == {
            "absent_in_package_1": ["package2"],
            "absent_in_package_2": ["package1"],
        }


def test_get_package_meta(client):
    with patch(
        "src.store.router.StoreService.get_package_meta"
    ) as mock_get_package_meta:
        mock_get_package_meta.return_value = PackageMeta(
            present=True,
            closure_size=0,
        )

        response = client.get("/store/store/package/package")

        assert response.status_code == 200
        assert response.json() == {"present": True, "closure_size": 0}
