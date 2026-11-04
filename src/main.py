import src.models
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.redis import redis_client
from src.auth.router import router as auth_router
from src.categories.router import router as category_router
from src.products.router import router as product_router
from src.merchant.router import router as merchant_router
from src.cart.router import router as cart_router
from src.orders.router import router as order_router
from src.addresses.router import router as address_router


@asynccontextmanager
async def lifespan(app_: FastAPI):
    print('project ishga tushdi')

    yield
    print('project toxtadi')
    await redis_client.aclose()


app = FastAPI(docs_url="/", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")

app.include_router(merchant_router, prefix="/api/v1")


app.include_router(order_router, prefix="/api/v1")
app.include_router(address_router, prefix="/api/v1")
