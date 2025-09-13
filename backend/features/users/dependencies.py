# features/users/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from .service import UserService

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# features/users/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from .service import UserService
from .models import UserUpdate, UserProfile, PasswordChange
from .dependencies import get_user_service
from features.auth.dependencies import (
    get_current_active_user,
    get_current_superuser
)
from features.auth.schemas import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
) -> UserProfile:
    """Get current user's profile"""
    return UserProfile.from_orm(current_user)

@router.put("/profile", response_model=UserProfile)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
) -> UserProfile:
    """Update current user's profile"""
    return await user_service.update_user_profile(current_user.id, user_data)

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Change current user's password"""
    await user_service.change_password(current_user.id, password_data)
    return {"message": "Password changed successfully"}

@router.delete("/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate current user's account"""
    await user_service.deactivate_user(current_user.id)
    return {"message": "Account deactivated successfully"}

# Admin endpoints
@router.get("/", response_model=List[UserProfile])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
) -> List[UserProfile]:
    """Get all users (admin only)"""
    return await user_service.get_all_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
) -> UserProfile:
    """Get user by ID (admin only)"""
    return await user_service.get_user_profile(user_id)

@router.put("/{user_id}", response_model=UserProfile)
async def update_user_by_id(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
) -> UserProfile:
    """Update user by ID (admin only)"""
    return await user_service.update_user_profile(user_id, user_data)

@router.delete("/{user_id}")
async def deactivate_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate user by ID (admin only)"""
    await user_service.deactivate_user(user_id)
    return {"message": f"User {user_id} deactivated successfully"}