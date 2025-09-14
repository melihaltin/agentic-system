from supabase import Client
from gotrue.errors import AuthApiError
from typing import Optional, Dict, Any
from .schemas import RegisterRequest, LoginRequest, ProfileUpdateRequest
from ..shared.database.supabase_client import supabase


class AuthRepository:
    def __init__(self, client: Client = supabase):
        self.client = client

    async def register_user(self, request: RegisterRequest) -> Dict[str, Any]:
        try:
            response = self.client.auth.sign_up(
                {
                    "email": request.email,
                    "password": request.password,
                    "options": {"data": {"full_name": request.full_name}},
                }
            )
            return response.dict()
        except AuthApiError as e:
            raise ValueError(f"Registration failed: {e.message}")

    async def login_user(self, request: LoginRequest) -> Dict[str, Any]:
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": request.email, "password": request.password}
            )
            return response.dict()
        except AuthApiError as e:
            raise ValueError(f"Login failed: {e.message}")

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        try:
            response = self.client.auth.refresh_session(refresh_token)
            return response.dict()
        except AuthApiError as e:
            raise ValueError(f"Token refresh failed: {e.message}")

    async def logout_user(self, access_token: str) -> bool:
        try:
            self.client.auth.sign_out(access_token)
            return True
        except AuthApiError:
            return False

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.client.table("user_profiles")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            return response.data
        except Exception:
            return None

    async def update_user_profile(
        self, user_id: str, request: ProfileUpdateRequest
    ) -> Dict[str, Any]:
        try:
            update_data = request.dict(exclude_unset=True)
            update_data["updated_at"] = "NOW()"

            response = (
                self.client.table("user_profiles")
                .update(update_data)
                .eq("id", user_id)
                .execute()
            )
            return response.data[0]
        except Exception as e:
            raise ValueError(f"Profile update failed: {str(e)}")

    async def change_password(self, access_token: str, new_password: str) -> bool:
        try:
            self.client.auth.update_user({"password": new_password}, access_token)
            return True
        except AuthApiError:
            return False
