from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import RegisterRequest, VerifyOTP, LoginResponse, NeedRegistrationResponse, CompleteRegistration
from auth.services import (
    check_verification_code,
    create_tokens,
    send_verification_code, create_registration_token, decode_token,
)
from core.database import get_db
from src.users.models import User
from users.schemas import UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_api(data: RegisterRequest):
    await send_verification_code(data.phone)

    return {
        "message": "Tasdiqlash kodi yuborildi",
        "phone": data.phone,
    }


@router.post("/verify-otp", response_model=LoginResponse | NeedRegistrationResponse, status_code=status.HTTP_200_OK)
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

    find_user = select(User).where(User.phone == data.phone)
    result = await db.execute(find_user)
    user = result.scalar_one_or_none()
    if user:
        tokens = create_tokens(user_id=str(user.id), phone=user.phone)
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            user=UserProfile.model_validate(user),
        )

    return NeedRegistrationResponse(
        registration_token=create_registration_token(data.phone)
    )


@router.post("/complete-registration", response_model=LoginResponse)
async def complete_registration_api(
        data: CompleteRegistration,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "registration":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Notogri token turi",
        )

    phone = payload["sub"]

    find_user = select(User).where(User.phone == phone)
    result = await db.execute(find_user)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            phone=phone,
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
        )
        db.add(user)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            result = await db.execute(find_user)
            user = result.scalar_one_or_none()
            if user is None:
                raise
        else:
            await db.refresh(user)

    tokens = create_tokens(user_id=str(user.id), phone=user.phone)
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        user=UserProfile.model_validate(user),
    )
