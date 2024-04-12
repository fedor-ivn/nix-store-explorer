import os

from fastapi_users.authentication import (
    CookieTransport,
    JWTStrategy,
    AuthenticationBackend,
)


cookie_transport = CookieTransport(cookie_max_age=3600)


SECRET = os.getenv("SECRET", "default_secret")


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy= lambda: JWTStrategy(secret=SECRET, lifetime_seconds=3600),
)
