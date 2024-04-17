from fastapi import FastAPI
import asyncio
import uvicorn

from store.router import router as store_router
from db.db import create_db_and_tables
from auth.auth import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead

app = FastAPI()

app.include_router(store_router)

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
