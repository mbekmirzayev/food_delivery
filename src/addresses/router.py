from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from addresses.models import Address
from addresses.schemas import AddressResponse, CreateAddress
from core.database import get_db
from core.dependencies import get_current_user_id

router = APIRouter(prefix="/address", tags=['address'])


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=AddressResponse)
async def address_create(
        data: CreateAddress,
        user_id: UUID = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)):
    address = Address(**data.model_dump(), user_id=user_id)
    db.add(address)
    await db.commit()
    await db.refresh(address)
    return address


@router.get('/list', response_model=List[AddressResponse], status_code=status.HTTP_200_OK)
async def get_address(
        user_id: UUID = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Address).where(Address.user_id == user_id).order_by(Address.created_at.desc()))
    return result.scalars().all()
