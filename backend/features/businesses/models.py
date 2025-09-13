from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


class BusinessBase(BaseModel):
    """Base business model."""
    email: EmailStr
    business_type: str = Field(..., description="Type of business (e.g., restaurant, car_rental, shopify)")
    business_name: str = Field(..., min_length=1, max_length=100, description="Business name")
    business_website: Optional[str] = Field(None, description="Business website URL")
    business_phone_number: Optional[str] = Field(None, description="Business phone number")
    
    @validator("business_website")
    def validate_website_url(cls, v):
        if v and not re.match(r'^https?://', v):
            v = f"https://{v}"
        return v
    
    @validator("business_phone_number")
    def validate_phone_number(cls, v):
        if v:
            # Remove all non-digit characters
            phone = re.sub(r'[^\d+]', '', v)
            if len(phone) < 10:
                raise ValueError("Phone number must be at least 10 digits")
        return v


class BusinessCreate(BusinessBase):
    """Business creation model."""
    password: str = Field(..., min_length=6, description="Password for Supabase auth")


class BusinessUpdate(BaseModel):
    """Business update model."""
    business_name: Optional[str] = Field(None, min_length=1, max_length=100)
    business_website: Optional[str] = None
    business_phone_number: Optional[str] = None
    
    @validator("business_website")
    def validate_website_url(cls, v):
        if v and not re.match(r'^https?://', v):
            v = f"https://{v}"
        return v


class BusinessResponse(BusinessBase):
    """Business response model."""
    id: UUID = Field(..., description="Business ID")
    created_at: datetime
    
    class Config:
        from_attributes = True


class BusinessListResponse(BaseModel):
    """Business list response model."""
    businesses: List[BusinessResponse]
    total: int
    page: int
    per_page: int


class BusinessAuthResponse(BaseModel):
    """Business authentication response."""
    business: BusinessResponse
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"