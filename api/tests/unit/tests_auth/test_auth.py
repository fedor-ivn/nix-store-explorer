from unittest.mock import patch
import importlib


def test_secret_default():
    from api.auth.auth import SECRET

    assert SECRET == "default_secret"


def test_secret_env():
    with patch.dict("os.environ", {"SECRET": "my_secret"}):
        import api.auth.auth

        importlib.reload(api.auth.auth)
        assert api.auth.auth.SECRET == "my_secret"


def test_auth_backend():
    import api.auth.auth

    importlib.reload(api.auth.auth)
    from api.auth.auth import auth_backend

    assert auth_backend.name == "jwt"
    assert auth_backend.transport.cookie_max_age == 3600
    assert auth_backend.get_strategy().secret == "default_secret"
    assert auth_backend.get_strategy().lifetime_seconds == 3600


def test_fastapi_users():
    from api.auth.auth import fastapi_users
    from auth.manager import get_user_manager

    assert fastapi_users.get_user_manager == get_user_manager
    assert fastapi_users.authenticator.backends[0].name == "jwt"
    assert fastapi_users.authenticator.backends[0].transport.cookie_max_age == 3600
    assert (
        fastapi_users.authenticator.backends[0].get_strategy().secret
        == "default_secret"
    )
    assert (
        fastapi_users.authenticator.backends[0].get_strategy().lifetime_seconds == 3600
    )
