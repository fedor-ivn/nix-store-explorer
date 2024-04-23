import os

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    CookieTransport,
    JWTStrategy,
    AuthenticationBackend,
)

from src.auth.manager import get_user_manager
from src.auth.schemas import User

cookie_transport = CookieTransport(cookie_max_age=3600)


SECRET = os.getenv("SECRET", "default_secret")


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=lambda: JWTStrategy(secret=SECRET, lifetime_seconds=3600),
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
