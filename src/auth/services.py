import json
import re
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status

from core.redis import redis_client
from core.config import settings

OTP_KEY_PREFIX = "otp"
LIMIT_KEY_PREFIX = "limit"
TEMP_USER_PREFIX = "temp_user"

OTP_TTL = 300
LIMIT_TTL = 60


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)

    if digits.startswith("998") and len(digits) == 12:
        return f"+{digits}"
    elif len(digits) == 9:
        return f"+998{digits}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notogri phone kiritildi example=> +998931970019",
        )


def get_otp_key(phone: str) -> str:
    return f"{OTP_KEY_PREFIX}:{phone}"


def get_limit_key(phone: str) -> str:
    return f"{LIMIT_KEY_PREFIX}:{phone}"


def get_temp_user_key(phone: str) -> str:
    return f"{TEMP_USER_PREFIX}:{phone}"


async def send_verification_code(phone: str) -> str:
    phone = normalize_phone(phone)
    limit_key = get_limit_key(phone)
    code_key = get_otp_key(phone)

    remaining = await redis_client.ttl(limit_key)
    if remaining and remaining > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f" {remaining} soniyadan keyn urinib koring",
        )

    code = str(secrets.randbelow(900000) + 100000)
    print(f"[DEBUG] OTP | phone={phone} | code={code}")

    await redis_client.setex(code_key, OTP_TTL, code)
    await redis_client.setex(limit_key, LIMIT_TTL, "1")

    return code


async def check_verification_code(phone: str, code: str) -> bool:
    phone = normalize_phone(phone)
    code_key = get_otp_key(phone)

    cached = await redis_client.get(code_key)

    print(f" key={code_key} | cached={cached} | input={code}")

    if cached is not None and str(cached) == str(code):
        await redis_client.delete(code_key, get_limit_key(phone))
        return True

    return False


async def save_temp_user(data: dict) -> None:
    phone = normalize_phone(data["phone"])
    key = get_temp_user_key(phone)
    await redis_client.setex(key, OTP_TTL, json.dumps(data))


async def get_temp_user(phone: str) -> dict | None:
    phone = normalize_phone(phone)
    key = get_temp_user_key(phone)
    raw_data = await redis_client.get(key)
    if raw_data:
        await redis_client.delete(key)
        return json.loads(raw_data)
    return None


def create_access_token(user_id: str, phone: str) -> str:
    payload = {
        "sub": str(user_id),
        "phone": phone,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_TIME),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_TIME),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_tokens(user_id: str, phone: str) -> dict:
    clean_phone = normalize_phone(phone)
    return {
        "access_token": create_access_token(user_id, clean_phone),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token muddati tugagan")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Noto'g'ri token")
