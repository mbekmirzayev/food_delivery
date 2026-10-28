from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, computed_field


class CartItemActionSchema(BaseModel):
    product_id: UUID
    quantity: int = Field(..., ge=0)


class CartProductItemList(BaseModel):
    id: UUID
    product_id: UUID
    merchant_id: UUID
    title: str
    price: Decimal
    quantity: int

    @computed_field
    @property
    def total_price(self) -> Decimal:
        return self.price * self.quantity

    model_config = ConfigDict(from_attributes=True)


class CartOutSchema(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    cart_items: List[CartProductItemList]

    @property
    def total_amount(self) -> Decimal:
        return sum((item.total_price for item in self.cart_items), Decimal("0.00"))
