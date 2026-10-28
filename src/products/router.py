from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database import get_db
from core.dependencies import is_admin
from src.products.models import Product
from src.products.schemas import ProductResponse, ProductCreateSchema

router = APIRouter(prefix="/product", tags=["product"])


@router.post("/create",
             status_code=status.HTTP_201_CREATED,
             response_model=ProductResponse,
             dependencies=[Depends(is_admin)])
async def create_product(
        data: ProductCreateSchema,
        db: AsyncSession = Depends(get_db)):
    slug = Product.make_slug(data.title)
    new_product = Product(
        category_id=data.category_id,
        merchant_id=data.merchant_id,
        title=data.title,
        description=data.description,
        image=data.image,
        price=data.price,
        is_active=data.is_active,
        slug=slug
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    return new_product


@router.get('/list',
            status_code=status.HTTP_200_OK,
            response_model=List[ProductResponse])
async def product_list(
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.is_active.is_(True)))
    return result.scalars().all()
