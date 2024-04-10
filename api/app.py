from fastapi import FastAPI

from store.router import router as store_router

app = FastAPI()

app.include_router(store_router)
