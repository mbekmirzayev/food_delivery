from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_user_id, get_current_merchant_id
from orders.schemas import UpdateOrderStatus
from src.orders.schemas import OrderResponse, OrderCreateSchema, OrderList
from src.orders.services import OrderService

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


"""                      ORDER STATUS CHANGE                """



@router.get('/merchant/list', response_model=List[OrderList], status_code=status.HTTP_200_OK)   # merchant orderlarining listi
async def merchant_order_list(
        db: AsyncSession = Depends(get_db),
        merchant_id : UUID = Depends(get_current_merchant_id),
        limit: int = Query(20, ge=1, le=50),
        offset: int = Query(0, ge=0)):
    return await OrderService.get_merchant_orders(db, merchant_id, limit, offset)

@router.post('/{order_id}/status', response_model=OrderResponse, status_code=status.HTTP_200_OK)    # order statusini accept qilish orderni merchant qabul qilishi
async def update_status(
        order_id : UUID,
        data: UpdateOrderStatus,
        db: AsyncSession = Depends(get_db),
        merchant_id : UUID = Depends(get_current_merchant_id),):

    return await OrderService.update_order_status_by_merchant(db = db, merchant_id= merchant_id, order_id = order_id, new_status = data.status)



@router.post('/{order_id}/cancel', response_model=OrderResponse)
async def cancel_order_by_customer(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    return await OrderService.cancel_order_by_customer(db, order_id, user_id)