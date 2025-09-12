from fastapi import APIRouter, Depends, status
from core.supabase_auth import SupabaseAuthService, get_supabase_auth_service, get_current_supabase_user
from features.users.models import UserCreate
from features.auth.models import LoginRequest
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


class SupabaseTokenResponse(BaseModel):
    """Supabase token response model."""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    user: Dict[str, Any]


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


@router.post("/supabase/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def supabase_register(
    user_data: UserCreate,
    auth_service: SupabaseAuthService = Depends(get_supabase_auth_service)
) -> Dict[str, Any]:
    """Register a new user with Supabase Auth."""
    return await auth_service.sign_up_with_email(user_data)


@router.post("/supabase/login", response_model=SupabaseTokenResponse)
async def supabase_login(
    login_data: LoginRequest,
    auth_service: SupabaseAuthService = Depends(get_supabase_auth_service)
) -> SupabaseTokenResponse:
    """Login with Supabase Auth."""
    result = await auth_service.sign_in_with_email(login_data.email, login_data.password)
    
    return SupabaseTokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        expires_in=result["expires_in"],
        user=result["user"].__dict__
    )


@router.post("/supabase/refresh", response_model=SupabaseTokenResponse)
async def supabase_refresh_token(
    refresh_data: RefreshRequest,
    auth_service: SupabaseAuthService = Depends(get_supabase_auth_service)
) -> SupabaseTokenResponse:
    """Refresh access token."""
    result = await auth_service.refresh_token(refresh_data.refresh_token)
    
    return SupabaseTokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        expires_in=result["expires_in"],
        user={}  # User info not returned in refresh
    )


@router.post("/supabase/logout")
async def supabase_logout(
    current_user: Dict[str, Any] = Depends(get_current_supabase_user),
    auth_service: SupabaseAuthService = Depends(get_supabase_auth_service)
) -> Dict[str, str]:
    """Logout from Supabase Auth."""
    # Extract token from the current user context or require it as parameter
    return await auth_service.sign_out("")


@router.get("/supabase/me")
async def get_supabase_current_user(
    current_user: Dict[str, Any] = Depends(get_current_supabase_user)
) -> Dict[str, Any]:
    """Get current user profile from Supabase."""
    return {
        "auth_user": current_user["auth_user"].__dict__,
        "profile": current_user["profile"]
    }


@router.put("/supabase/profile")
async def update_supabase_profile(
    profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_supabase_user),
    auth_service: SupabaseAuthService = Depends(get_supabase_auth_service)
) -> Dict[str, Any]:
    """Update user profile in Supabase."""
    user_id = current_user["auth_user"].id
    return await auth_service.update_user_profile(user_id, profile_data)
