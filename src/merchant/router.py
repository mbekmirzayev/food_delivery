from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database import get_db
from core.dependencies import is_admin
from src.merchant.models import Merchant
from src.merchant.schemas import MerchantResponse, MerchantCreateSchema

router = APIRouter(prefix="/merchant", tags=["merchant"])


@router.post('/create',
             status_code=status.HTTP_201_CREATED,
             response_model=MerchantResponse,
             dependencies=[Depends(is_admin)])
async def create_merchant(
        data: MerchantCreateSchema,
        db: AsyncSession = Depends(get_db)
):
    existing_merchant = await db.scalar(select(Merchant).where(Merchant.business_name == data.business_name))
    if existing_merchant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bunday nomli business name mavjud")

    slug = Merchant.make_slug(data.business_name)
    new_merchant = Merchant(
        business_name=data.business_name,
        user_id=data.user_id,
        slug=slug
    )
    db.add(new_merchant)
    await db.commit()
    await db.refresh(new_merchant)

    return new_merchant


@router.get('/list',
            status_code=status.HTTP_200_OK,
            response_model=List[MerchantResponse])
async def merchant_list(
        db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Merchant))
    return res.scalars().all()
