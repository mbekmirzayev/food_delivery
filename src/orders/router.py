from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user_id
from orders.schemas import OrderResponse, OrderCreateSchema, OrderList
from orders.services import OrderService

router = APIRouter(prefix="/order", tags=["Order"])


@router.post('/create', response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
        data: OrderCreateSchema,
        db: AsyncSession = Depends(get_db),
        user_id: UUID = Depends(get_current_user_id)):
    return await OrderService.create_from_cart(data, db, user_id)


@router.get('/list', response_model=List[OrderList], status_code=status.HTTP_200_OK)
async def list_order(
        db: AsyncSession = Depends(get_db),
        user_id : UUID = Depends(get_current_user_id),
        limit: int = Query(20, ge=1, le =100),
        offset: int = Query(0, ge=0)):
    return await OrderService.order_list(db, user_id, limit, offset)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    return await OrderService.get_user_order(db, order_id, user_id)
