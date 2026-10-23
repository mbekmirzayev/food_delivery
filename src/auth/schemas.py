import enum

from pydantic import BaseModel, Field
from pydantic import field_validator

from auth.services import normalize_phone


class RoleEnum(str, enum.Enum):
    CUSTOMER = "customer"
    COURIER = "courier"
    MERCHANT = 'merchant'


class RegisterRequest(BaseModel):
    phone: str = Field(max_length=20, default="+998901234567")
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    role: RoleEnum = Field(default=RoleEnum.CUSTOMER)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)


class VerifyOTP(BaseModel):
    phone: str = Field(max_length=20, default="+998901234567")
    otp: str = Field(min_length=5, max_length=6)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator('otp')
    @classmethod
    def validate_otp(cls, otp: str) -> str:
        if not otp.isdigit():
            raise ValueError("bir martalik code faqat raqam bolishi kere")
        return otp
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    message: str
    role: RoleEnum
