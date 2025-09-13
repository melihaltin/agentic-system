# features/users/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from typing import Optional, List

from features.auth.schemas import User
from .models import UserUpdate, UserProfile, PasswordChange
from core.security import verify_password, get_password_hash

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile by ID"""
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile.from_orm(user)

    async def update_user_profile(self, user_id: str, user_data: UserUpdate) -> UserProfile:
        """Update user profile"""
        # Check if username is already taken (if provided)
        if user_data.username:
            existing_user = await self.db.execute(
                select(User).filter(
                    User.username == user_data.username,
                    User.id != user_id
                )
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Update user
        update_data = user_data.dict(exclude_unset=True)
        if update_data:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            await self.db.commit()
        
        return await self.get_user_profile(user_id)

    async def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        """Change user password"""
        # Get current user
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_hashed_password = get_password_hash(password_data.new_password)
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(hashed_password=new_hashed_password)
        )
        await self.db.commit()
        
        return True

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return True

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        """Get all users (admin only)"""
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()
        return [UserProfile.from_orm(user) for user in users]