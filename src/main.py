import src.models
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.redis import redis_client
from src.auth.router import router as auth_router




@asynccontextmanager
async def lifespan(app_: FastAPI):
    print('project ishga tushdi')

    yield
    print('project toxtadi')
    await redis_client.aclose()


app = FastAPI(docs_url="/", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1")



