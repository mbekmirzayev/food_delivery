import secrets
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException

from addresses.models import Address
from cart.models import Cart, CartItem
from cart.services import CartService
from core.database import get_db
from core.dependencies import get_current_user_id
from orders.models import Order, OrderItem
from orders.schemas import OrderCreateSchema


def generate_order_number() -> str:
    num = secrets.randbelow(900_000) + 100_000
    num = str(num)
    return f"{num[:3]}-{num[3:]}"


class OrderService:
    @classmethod
    async def create_from_cart(cls,
                               data: OrderCreateSchema,
                               db: AsyncSession = Depends(get_db),
                               user_id: UUID = Depends(get_current_user_id)):

        cart = await  CartService.get_or_create_cart(db, user_id)
        if not cart.cart_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="savat bosh")

        address = await db.get(Address, data.delivery_address_id)
        if not address or Address.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Address mavlud emas yoki bu addres sizga tegishli emas")

        merchant_id = Cart.cart_items[0].product.merchant_id
        items: List[OrderItem] = []
        total = Decimal("0.00")
        order_num = generate_order_number()
        for ci in cart.cart_items:
            product = ci.products
            # if product is None or product.merchant_id != merchant_id:
            #     raise HTTPException(status.HTTP_400_BAD_REQUEST, "Savatdagi mahsulot yaroqsiz")

            line_total = product.price * ci.quantity
            total += line_total
            items.append(OrderItem(
                product_id=product.id,
                product_title=product.title,
                quantity=ci.quantity,
                total_price=line_total,
                unit_price=product.price
            ))
            order = Order(
                merchant_id=merchant_id,
                user_id=user_id,
                delivery_address_id=address.id,
                order_number=order_num,
                total_amount=total,
                notes=data.notes,
                order_items=items)
            db.add(order)
            await db.flush()
            order_id = order.id
            await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
            await db.commit()

            return await cls.get_order(db, order_id)

    @classmethod
    async def get_order(cls, db: AsyncSession, order_id: UUID):
        res = await db.execute(select(Order)
                               .where(Order.id == order_id)
                               .options(selectinload(Order.order_items))
                               .execution_options(populate_existing=True))
        order = res.scalar_one_or_none()
        if not order:
            HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail="order topilmadi")
        return order

    @classmethod
    async def get_user_order(cls, db: AsyncSession, order_id: UUID, user_id: UUID):
        order = await cls.get_order(db, order_id)

        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order topilmadi")
        return order

    @classmethod
    async def order_list(cls, db: AsyncSession, user_id: UUID, limit: int = 20, offset: int = 0):
        result = await db.execute(select(Order)
                       .where(Order.user_id == user_id)
                       .order_by(Order.created_at.desc())
                        .limit(limit).offset(offset))
        return result.scalars().all()
