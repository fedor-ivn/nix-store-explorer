import pytest
from auth.manager import get_user_manager, UserManager
from auth.schemas import User
from unittest.mock import patch


@pytest.mark.asyncio
async def test_on_after_register():
    with patch("auth.manager.print") as mock_print:
        manager = UserManager(None)
        await manager.on_after_register(User(id=1))
        mock_print.assert_called_with("User 1 has registered.")


@pytest.mark.asyncio
async def test_get_user_manager():
    async for manager in get_user_manager():
        assert isinstance(manager, UserManager)
