from fastapi import APIRouter, Depends, status
from features.auth.service import AuthService
from features.auth.models import LoginRequest, TokenResponse
from features.auth.dependencies import get_auth_service
from features.users.models import UserCreate, UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Login with email and password to get access token."""
    return await auth_service.login(login_data)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Register a new user account."""
    return await auth_service.register(user_data)


@router.post("/logout")
async def logout() -> dict:
    """Logout endpoint (client-side token removal)."""
    return {
        "message": "Successfully logged out. Please remove the token from client storage."
    }
