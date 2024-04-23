from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from .database import get_user_db
from .schemas import User


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
