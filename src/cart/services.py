from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from src.cart.models import Cart, CartItem
from src.cart.schema import CartItemActionSchema
from src.products.models import Product


class CartService:
    CART_EXPIRE_TIME = 5
    MAX_CART_ITEMS = 50

    @classmethod
    async def _fetch_cart_with_cart_items(cls, db: AsyncSession, user_id: UUID) -> Cart | None:
        existing_items = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.cart_items)
                     .selectinload(CartItem.products))
            .execution_options(populate_existing=True))

        result = await db.execute(existing_items)
        return result.scalar_one_or_none()

    @classmethod
    async def get_or_create_cart(cls, db: AsyncSession, user_id: UUID) -> Cart:
        cart = await cls._fetch_cart_with_cart_items(db, user_id)

        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.commit()
            return await cls._fetch_cart_with_cart_items(db, user_id)

        if cart.cart_items:
            latest_time = max(item.created_at for item in cart.cart_items)
            now = datetime.now(timezone.utc)

            if now - latest_time > timedelta(minutes=cls.CART_EXPIRE_TIME):
                await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
                await db.commit()
                return await cls._fetch_cart_with_cart_items(db, user_id)

        return cart

    @classmethod
    async def set_item_quantity(cls, db: AsyncSession, user_id: UUID, data: CartItemActionSchema) -> Cart:
        cart = await cls.get_or_create_cart(db, user_id)

        product = await db.get(Product, data.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Mahsulot topilmadi")

        if data.quantity == 0:
            await db.execute(delete(CartItem)
                             .where(CartItem.cart_id == cart.id,
                                    CartItem.product_id == data.product_id))

            await db.commit()
            return await cls._fetch_cart_with_cart_items(db, user_id)

        if cart.cart_items:
            current_merchant_id = cart.cart_items[0].products.merchant_id
            if current_merchant_id != product.merchant_id:
                await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
                cart = await cls._fetch_cart_with_cart_items(db, user_id)
        existing_item = next((item for item in cart.cart_items if item.product_id == data.product_id), None)

        if existing_item:
            existing_item.quantity = data.quantity

        else:
            if len(cart.cart_items) >= cls.MAX_CART_ITEMS:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Savatda 50tadan kop mahsulot bolishi mumkin emas")
            new_item = CartItem(cart_id=cart.id,
                                product_id=data.product_id,
                                quantity=data.quantity)

            db.add(new_item)
        await db.commit()
        return await cls._fetch_cart_with_cart_items(db, user_id)

    @classmethod
    async def clear_cart(cls, db: AsyncSession, user_id: UUID) -> Cart:
        cart = await cls.get_or_create_cart(db, user_id)
        await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        await db.commit()
        return await cls._fetch_cart_with_cart_items(db, user_id)
