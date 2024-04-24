from typing import Tuple, Optional
import bcrypt

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.password import PasswordHelperProtocol

from auth.database import get_user_db
from auth.schemas import User


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")


class PasswordHelper(PasswordHelperProtocol):
    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def generate(self) -> str:
        return bcrypt.gensalt().decode()

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> Tuple[bool, str]:
        return (
            bcrypt.checkpw(plain_password.encode(), hashed_password.encode()),
            hashed_password,
        )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db, PasswordHelper())
