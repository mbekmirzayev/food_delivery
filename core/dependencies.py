from sqlalchemy import select
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from src.merchant.models import Merchant
from src.auth.services import decode_token
from src.users.models import User

bearer_scheme = HTTPBearer()


async def get_current_user_payload(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get('type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Faqat access token qabul qiladi")
    return payload


async def is_admin(payload: dict = Depends(get_current_user_payload)) -> dict:
    if payload.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Sizda tegishli ruxsat yoq")
    return payload


async def get_current_user_id(payload: dict = Depends(get_current_user_payload)) -> UUID:
    raw = payload.get('sub')
    if raw is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token user id yoq")

    return UUID(raw)

async def get_current_merchant_id(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db) ) -> UUID:
    user = await db.get(User, user_id)
    if not user or user.role != User.UserRole.MERCHANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amalni faqat merchant bajara oladi!"
        )

    res = await db.execute(select(Merchant).where(Merchant.user_id == user_id))
    merchant = res.scalar_one_or_none()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sizda hali Merchant  profili ochilmagan!"
        )

    return merchant.id