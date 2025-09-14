from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class CompanyProfile(BaseModel):
    id: str
    user_id: str
    company_name: str
    phone_number: str
    business_category: str
    platform: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime


class UserProfile(BaseModel):
    id: str
    user_id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.USER
    created_at: datetime
    updated_at: datetime
    company: Optional[CompanyProfile] = None


class AuthUser(BaseModel):
    id: str
    email: EmailStr
    profile: Optional[UserProfile] = None
