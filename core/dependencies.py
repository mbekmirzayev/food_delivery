from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from src.auth.services import decode_token

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
