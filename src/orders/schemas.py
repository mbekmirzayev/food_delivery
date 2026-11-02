from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.orders.models import OrderStatus


class OrderCreateSchema(BaseModel):
    delivery_address_id: UUID
    notes: str


class OrderItemsResponse(BaseModel):
    id: UUID
    courier_id: Optional[UUID] = None
    product_title : str
    unit_price : Decimal
    quantity : int
    total_price : Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    courier_id: Optional[UUID] = None
    total_amount: Decimal
    delivery_fee: Decimal
    status: OrderStatus
    order_number: str
    created_at: datetime
    order_items : List[OrderItemsResponse] = []
    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    id: UUID
    merchant_id: UUID
    status: OrderStatus
    created_at: datetime
    total_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class UpdateOrderStatus(BaseModel):
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)