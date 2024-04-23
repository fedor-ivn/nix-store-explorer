import os

from auth.manager import get_user_manager
from auth.schemas import User
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)

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
