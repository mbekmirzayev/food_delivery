import enum
from typing import Literal

from pydantic import BaseModel, Field
from pydantic import field_validator

from src.auth.services import normalize_phone
from src.users.schemas import UserProfile, RoleEnum


class RegisterRequest(BaseModel):
    phone: str = Field(max_length=20, default="+998901234567")


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

class CompleteRegistration(BaseModel):
    first_name:str = Field(min_length=3, max_length=25)
    last_name:str = Field(min_length=3, max_length=25)
    role:RoleEnum=RoleEnum.CUSTOMER

class LoginResponse(BaseModel):
    is_new_user: Literal[False] = False
    token_type: str = "bearer"
    access_token: str
    refresh_token: str
    user: UserProfile


class NeedRegistrationResponse(BaseModel):
    is_new_user: Literal[True] = True
    registration_token: str