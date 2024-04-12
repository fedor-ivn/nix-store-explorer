from fastapi import FastAPI
from fastapi import FastAPI
from fastapi_users import fastapi_users, FastAPIUsers
import asyncio
import uvicorn

from store.router import router as store_router
from auth.database import User, create_db_and_tables
from auth.auth import auth_backend
from auth.schemas import UserCreate, UserRead
from auth.manager import get_user_manager

app = FastAPI()

app.include_router(store_router)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


if __name__ == "__main__":
    asyncio.run(create_db_and_tables())

    uvicorn.run(app, host="localhost", port=8000)
