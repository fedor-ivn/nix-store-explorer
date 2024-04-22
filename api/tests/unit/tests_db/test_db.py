from unittest.mock import patch
import importlib
import pytest
from db.db import create_db_and_tables, get_async_session


def test_database_url_default():
    from db.db import DATABASE_URL

    assert DATABASE_URL == "sqlite+aiosqlite:///./database.db"


def test_database_url_env():
    with patch.dict("os.environ", {"DATABASE_URL": "sqlite+aiosqlite:///./test.db"}):
        import db.db

        importlib.reload(db.db)
        from db.db import DATABASE_URL

        assert DATABASE_URL == "sqlite+aiosqlite:///./test.db"


@pytest.mark.asyncio
async def test_create_db_and_tables():
    with patch("db.db.Base.metadata.create_all") as mock_create_all:
        await create_db_and_tables()
        mock_create_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_async_session():
    with patch("db.db.async_session_maker") as mock_async_session_maker:
        async for _ in get_async_session():
            mock_async_session_maker.assert_called_once()
