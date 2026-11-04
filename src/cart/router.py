from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from cart.schema import CartItemActionSchema
from src.cart.schema import CartOutSchema, CartProductItemList
from src.cart.services import CartService
from core.database import get_db
from core.dependencies import get_current_user_payload, get_current_user_id
from src.users.models import User

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("",
            response_model=CartOutSchema,
            status_code=status.HTTP_200_OK)
async def get_my_cart(db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user_id)):
    return await CartService.get_or_create_cart(db, current_user)


@router.put('/items',
            response_model=CartOutSchema,
            status_code=status.HTTP_200_OK)
async def update_cart_items(
        data: CartItemActionSchema,
        db: AsyncSession = Depends(get_db),
        user_id: User = Depends(get_current_user_id)):
    return await CartService.set_item_quantity(db, user_id, data)

@router.delete('/clear',
               response_model=CartOutSchema,
               status_code=status.HTTP_200_OK)
async def clear_cart(db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user_payload)):
    return await CartService.clear_cart(db, current_user['sub'])