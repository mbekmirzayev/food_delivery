import src.models
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.redis import redis_client
from src.auth.router import router as auth_router
from src.categories.router import router as category_router
from src.products.router import router as product_router
from src.merchant.router import router as merchant_router
from src.cart.router import router as cart_router


@asynccontextmanager
async def lifespan(app_: FastAPI):
    print('project ishga tushdi')

    yield
    print('project toxtadi')
    await redis_client.aclose()


app = FastAPI(docs_url="/", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")

app.include_router(merchant_router, prefix="/api/v1")
