# features/users/models.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v



