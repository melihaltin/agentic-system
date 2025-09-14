from fastapi import APIRouter, Depends, status
from .service import AuthService
from .schemas import (
    RegisterRequest,
    BusinessRegistrationRequest,
    LoginRequest,
    AuthResponse,
    ProfileUpdateRequest,
    ChangePasswordRequest,
)
from .dependencies import get_auth_service, get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    return await auth_service.register(request)


@router.post(
    "/register/business",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_business(
    request: BusinessRegistrationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new business user with company profile"""
    try:
        print(f"DEBUG: Received business registration request: {request}")
        print(f"DEBUG: Request type: {type(request)}")
        print(f"DEBUG: Request dict: {request.dict()}")
        return await auth_service.register_business(request)
    except Exception as e:
        print(f"DEBUG: Exception in register_business: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        raise e


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Login user"""
    return await auth_service.login(request)


@router.post("/refresh")
async def refresh_token(
    refresh_token: str, auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    return await auth_service.refresh_token(refresh_token)


@router.post("/logout")
async def logout(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: dict = Depends(get_current_active_user),
):
    """Logout user"""
    # Access token'ı header'dan al
    return await auth_service.logout("dummy_token")  # Implementation'da düzeltilecek


@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get user profile"""
    return await auth_service.get_profile(current_user["id"])


@router.put("/profile")
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update user profile"""
    return await auth_service.update_profile(current_user["id"], request)


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Change user password"""
    return await auth_service.change_password("dummy_token", request)
