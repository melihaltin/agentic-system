from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(
        ..., min_length=3, max_length=50, description="Unique username"
    )
    full_name: Optional[str] = Field(
        None, max_length=100, description="User's full name"
    )
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(
        ..., min_length=8, description="User password (min 8 characters)"
    )


class UserUpdate(BaseModel):
    """User update model with optional fields."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Unique username"
    )
    full_name: Optional[str] = Field(
        None, max_length=100, description="User's full name"
    )
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")


class UserResponse(UserBase):
    """User response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether user account is active")
    is_superuser: bool = Field(..., description="Whether user has admin privileges")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserPublic(BaseModel):
    """Public user information (limited fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="User's full name")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")
    bio: Optional[str] = Field(None, description="User biography")
    created_at: datetime = Field(..., description="Account creation timestamp")


class UserLogin(BaseModel):
    """User login model."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class PasswordChange(BaseModel):
    """Password change model."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )


class UserListResponse(BaseModel):
    """Paginated user list response."""

    users: list[UserPublic] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")
