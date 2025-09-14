from fastapi import HTTPException, status
from .repository import AuthRepository
from .schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    ProfileUpdateRequest,
    ChangePasswordRequest,
)
from typing import Dict, Any


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def register(self, request: RegisterRequest) -> AuthResponse:
        try:
            response = await self.repository.register_user(request)

            if not response.get("user"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed",
                )

            return AuthResponse(
                user=response["user"],
                access_token=response["session"]["access_token"],
                refresh_token=response["session"]["refresh_token"],
                expires_in=response["session"]["expires_in"],
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def login(self, request: LoginRequest) -> AuthResponse:
        try:
            response = await self.repository.login_user(request)

            if not response.get("user"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            return AuthResponse(
                user=response["user"],
                access_token=response["session"]["access_token"],
                refresh_token=response["session"]["refresh_token"],
                expires_in=response["session"]["expires_in"],
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        try:
            response = await self.repository.refresh_token(refresh_token)

            return AuthResponse(
                user=response["user"],
                access_token=response["session"]["access_token"],
                refresh_token=response["session"]["refresh_token"],
                expires_in=response["session"]["expires_in"],
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    async def logout(self, access_token: str) -> Dict[str, str]:
        success = await self.repository.logout_user(access_token)
        if success:
            return {"message": "Successfully logged out"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed"
        )

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        profile = await self.repository.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )
        return profile

    async def update_profile(
        self, user_id: str, request: ProfileUpdateRequest
    ) -> Dict[str, Any]:
        try:
            profile = await self.repository.update_user_profile(user_id, request)
            return profile
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def change_password(
        self, access_token: str, request: ChangePasswordRequest
    ) -> Dict[str, str]:
        # İlk olarak mevcut şifreyi kontrol et (login ile)
        # Bu basit implementasyonda bu adımı atlıyoruz

        success = await self.repository.change_password(
            access_token, request.new_password
        )
        if success:
            return {"message": "Password changed successfully"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password change failed"
        )
