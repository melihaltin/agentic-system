from fastapi import HTTPException, status
from features.users.repository import UserRepository
from features.users.models import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPublic,
    UserListResponse,
    PasswordChange,
)
from features.users.schemas import User
from core.security import get_password_hash, verify_password
from core.config import settings

import structlog

logger = structlog.get_logger()


class UserService:
    """Service layer for user operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user with validation."""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        existing_username = await self.user_repository.get_by_username(
            user_data.username
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists",
            )

        try:
            user = await self.user_repository.create(user_data)
            logger.info(f"New user created: {user.email}")
            return UserResponse.model_validate(user)

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Get user by ID."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserResponse.model_validate(user)

    async def get_public_user_by_id(self, user_id: int) -> UserPublic:
        """Get public user info by ID."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserPublic.model_validate(user)

    async def get_user_by_username(self, username: str) -> UserPublic:
        """Get public user info by username."""
        user = await self.user_repository.get_by_username(username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserPublic.model_validate(user)

    async def get_users(self, page: int = 1, per_page: int = None) -> UserListResponse:
        """Get paginated list of users."""
        if per_page is None:
            per_page = settings.default_page_size

        if per_page > settings.max_page_size:
            per_page = settings.max_page_size

        if page < 1:
            page = 1

        skip = (page - 1) * per_page

        users = await self.user_repository.get_all(
            skip=skip, limit=per_page, active_only=True
        )
        total = await self.user_repository.count_all(active_only=True)

        user_list = [UserPublic.model_validate(user) for user in users]

        has_next = (skip + per_page) < total
        has_prev = page > 1

        return UserListResponse(
            users=user_list,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev,
        )

    async def update_user(
        self, user_id: int, user_data: UserUpdate, current_user: User
    ) -> UserResponse:
        """Update user information."""
        # Check if user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check permissions (user can only update their own profile unless they're admin)
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this user",
            )

        # Check for username/email conflicts if they're being updated
        if user_data.email and user_data.email != user.email:
            existing_email = await self.user_repository.get_by_email(user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists",
                )

        if user_data.username and user_data.username != user.username:
            existing_username = await self.user_repository.get_by_username(
                user_data.username
            )
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this username already exists",
                )

        try:
            updated_user = await self.user_repository.update(user_id, user_data)
            logger.info(f"User updated: {updated_user.email}")
            return UserResponse.model_validate(updated_user)

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def change_password(
        self, user_id: int, password_data: PasswordChange, current_user: User
    ) -> dict:
        """Change user password."""
        # Check if user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check permissions
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to change this user's password",
            )

        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password",
            )

        # Update password
        new_hashed_password = get_password_hash(password_data.new_password)
        await self.user_repository.update(
            user_id, UserUpdate(hashed_password=new_hashed_password)
        )

        logger.info(f"Password changed for user: {user.email}")
        return {"message": "Password updated successfully"}

    async def delete_user(self, user_id: int, current_user: User) -> dict:
        """Deactivate user (soft delete)."""
        # Check if user exists
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check permissions (admin only or user deleting their own account)
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this user",
            )

        success = await self.user_repository.delete(user_id)
        if success:
            logger.info(f"User deactivated: {user.email}")
            return {"message": "User deactivated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate user",
            )
