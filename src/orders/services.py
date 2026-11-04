import secrets
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException

from core.database import get_db
from core.dependencies import get_current_user_id
from src.addresses.models import Address
from src.cart.models import CartItem
from src.cart.services import CartService
from src.orders.models import Order, OrderItem, OrderStatus
from src.orders.schemas import OrderCreateSchema


def generate_order_number() -> str:
    num = secrets.randbelow(900_000) + 100_000
    num = str(num)
    return f"{num[:3]}-{num[3:]}"

    """
    Order statuslari tartiblangan va belgilangan shaklda ozgarishi lozim
    Pending statusidan togridan togri Deliveredga ozgara olmaydi
    """
MERCHANT_STATUS_TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.CANCELLED, OrderStatus.CONFIRMED],
        OrderStatus.CONFIRMED: [OrderStatus.READY, OrderStatus.CANCELLED],
        OrderStatus.READY: [OrderStatus.ON_THE_WAY, OrderStatus.CANCELLED],
        OrderStatus.ON_THE_WAY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: [],
    }
COURIER_STATUS_TRANSITIONS = {
    OrderStatus.READY: [OrderStatus.ON_THE_WAY, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
}

class OrderService:


    @classmethod
    async def create_from_cart(cls,
                               data: OrderCreateSchema,
                               db: AsyncSession = Depends(get_db),
                               user_id: UUID = Depends(get_current_user_id)):

        # userni savati bolsa olib keladi aks holda yangi yaratadi
        cart = await  CartService.get_or_create_cart(db, user_id)
        if not cart.cart_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="savat bosh")

        # schemada delivery_address_id olib keladi
        address = await db.get(Address, data.delivery_address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Address mavlud emas yoki bu addres sizga tegishli emas")

        """ 
        savatda faqatgina bir merchantning mahsulotlari bolishi mumkin shuning uchun faqat product[0]
        tekshirilgan merchant_id olinayotkanda
        """

        merchant_id = cart.cart_items[0].products.merchant_id
        items: List[OrderItem] = []
        total = Decimal("0.00")
        order_num = generate_order_number()
        for ci in cart.cart_items:
            product = ci.products
            # if product is None or product.merchant_id != merchant_id:
            #     raise HTTPException(status.HTTP_400_BAD_REQUEST, "Savatdagi mahsulot yaroqsiz")

            line_total = product.price * ci.quantity  # faqatgina bitta mahsulotni qatorini oladi
            total += line_total  # barcha orderni narxi
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
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

    """                     MERCHANT                    """

    @classmethod
    async def get_merchant_orders(cls,
                                  db: AsyncSession,
                                  merchant_id: UUID,
                                  limit: int = 20,
                                  offset: int = 0,
                                  ):
        result = await db.execute(select(Order)
                                  .where(Order.merchant_id == merchant_id)
                                  .order_by(Order.created_at.desc())
                                  .limit(limit).offset(offset))

        return result.scalars().all()

    @classmethod
    async def update_order_status_by_merchant(cls,
                          db: AsyncSession,
                          merchant_id: UUID,
                          order_id: UUID,
                          new_status: OrderStatus):

        order = await cls.get_order(db, order_id)
        if order.merchant_id != merchant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Bu zakaz sizni dokongizga tegisglimas")


        allowed_status = MERCHANT_STATUS_TRANSITIONS.get(order.status, [])

        if new_status not in  allowed_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="orderni bu statusga otkazib bolmaydi")
        order.status = new_status
        await db.commit()

        return await cls.get_order(db, order_id)



    @classmethod
    async def cancel_order_by_customer(cls,
                              db: AsyncSession,
                              user_id: UUID,
                              order_id: UUID):
        order = await cls.get_order(db, order_id)
        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Bu zakaz sizga tegisglimas")
        allowed_cancel_status = [
            OrderStatus.PENDING]
            # OrderStatus.CONFIRMED]

        if order.status not in allowed_cancel_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Orderni bekor qila olmaysi")

        order.status = OrderStatus.CANCELLED
        await db.commit()

        return await cls.get_order(db, order_id)

    @classmethod
    async def cancel_order_by_courier(cls,
                                       db: AsyncSession,
                                       courier_id: UUID,
                                       order_id: UUID):
        order = await cls.get_order(db, order_id)
        if order.courier_id != courier_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Bu zakaz sizga tegisglimas")
        allowed_cancel_status = [
            OrderStatus.READY,
            OrderStatus.ON_THE_WAY ]

        if order.status not in allowed_cancel_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Orderni bekor qila olmaysi")

        order.courier_id = None
        order.status = OrderStatus.READY
        await db.commit()

        return await cls.get_order(db, order_id)