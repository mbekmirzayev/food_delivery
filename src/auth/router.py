from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import RegisterRequest, TokenResponse, VerifyOTP
from auth.services import (
    check_verification_code,
    create_tokens,
    get_temp_user,
    save_temp_user,
    send_verification_code,
)
from core.database import get_db

from src.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_api(data: RegisterRequest):
    await send_verification_code(data.phone)

    await save_temp_user(data.model_dump())

    return {
        "message": "Tasdiqlash kodi yuborildi",
        "phone": data.phone,
    }


@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def verify_code_api(
        data: VerifyOTP,
        db: AsyncSession = Depends(get_db),
):

    is_valid = await check_verification_code(data.phone, data.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kod notogri yoki eskirgan",
        )


    stmt = select(User).where(User.phone == data.phone)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        temp_data = await get_temp_user(data.phone)
        if not temp_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ro'yxatdan o'tish ma'lumotlari topilmadi. Qaytadan /register qiling.",
            )

        user = User(
            phone=data.phone,
            first_name=temp_data["first_name"],
            last_name=temp_data["last_name"],
            role=temp_data["role"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        msg = "Muvaffaqiyatli ro'yxatdan o'tdingiz"
    else:

        await get_temp_user(data.phone)
        msg = "Tizimga muvaffaqiyatli kirdingiz"

    tokens = create_tokens(user_id=str(user.id), phone=user.phone)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        message=msg,
        role=user.role,
    )