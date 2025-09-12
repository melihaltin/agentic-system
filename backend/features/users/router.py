from fastapi import APIRouter, Depends, Query, status
from features.users.service import UserService
from features.users.models import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPublic,
    UserListResponse,
    PasswordChange,
)
from features.users.dependencies import get_user_service
from features.users.schemas import User
from core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user account."""
    return await user_service.create_user(user_data)


@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page"),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """Get paginated list of users."""
    return await user_service.get_users(page=page, per_page=per_page)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Get current user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update current user's profile."""
    return await user_service.update_user(current_user.id, user_data, current_user)


@router.post("/me/change-password")
async def change_current_user_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    """Change current user's password."""
    return await user_service.change_password(
        current_user.id, password_data, current_user
    )


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    """Deactivate current user's account."""
    return await user_service.delete_user(current_user.id, current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get user by ID (admin only or own profile)."""
    if user_id != current_user.id and not current_user.is_superuser:
        # Return public profile for non-admin users viewing others
        public_user = await user_service.get_public_user_by_id(user_id)
        return UserResponse.model_validate(public_user)

    return await user_service.get_user_by_id(user_id)


@router.get("/username/{username}", response_model=UserPublic)
async def get_user_by_username(
    username: str, user_service: UserService = Depends(get_user_service)
) -> UserPublic:
    """Get public user profile by username."""
    return await user_service.get_user_by_username(username)


@router.get("/public/{user_id}", response_model=UserPublic)
async def get_public_user_profile(
    user_id: int, user_service: UserService = Depends(get_user_service)
) -> UserPublic:
    """Get public user profile by ID."""
    return await user_service.get_public_user_by_id(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update user (admin only or own profile)."""
    return await user_service.update_user(user_id, user_data, current_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    """Deactivate user (admin only or own account)."""
    return await user_service.delete_user(user_id, current_user)
