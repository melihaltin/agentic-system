from pydantic import BaseModel, EmailStr, validator
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class BusinessRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str
    phone_number: str
    business_category: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

    @validator("company_name")
    def validate_company_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters long")
        return v.strip()

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Phone number must be at least 10 characters long")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: dict
    access_token: str
    refresh_token: str
    expires_in: int


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    business_category: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
