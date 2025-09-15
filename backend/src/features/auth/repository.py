from supabase import Client
from gotrue.errors import AuthApiError
from typing import Optional, Dict, Any
from .schemas import (
    RegisterRequest,
    BusinessRegistrationRequest,
    LoginRequest,
    ProfileUpdateRequest,
)
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

    async def register_business_user(
        self, request: BusinessRegistrationRequest
    ) -> Dict[str, Any]:
        try:
            print(f"DEBUG: Attempting admin user creation for: {request.email}")
            # Use admin API to create user without email confirmation
            admin_response = self.client.auth.admin.create_user(
                {
                    "email": request.email,
                    "password": request.password,
                    "user_metadata": {"full_name": request.full_name},
                    "email_confirm": True,  # Admin API can set user as confirmed
                }
            )
            print(f"DEBUG: Admin response: {admin_response}")

            if not admin_response.user:
                print(f"DEBUG: No user in admin response")
                raise ValueError("User creation failed")

            # Since admin API doesn't return session, we need to sign in the user
            auth_response = self.client.auth.sign_in_with_password(
                {"email": request.email, "password": request.password}
            )

            if not auth_response.user:
                raise ValueError("User creation failed")

            # Create company profile
            company_data = {
                "user_id": auth_response.user.id,
                "company_name": request.company_name,
                "phone_number": request.phone_number,
                "business_category": request.business_category,
            }

            try:
                company_response = (
                    self.client.table("company_profiles").insert(company_data).execute()
                )

                if not company_response.data:
                    print(
                        f"Warning: Company profile creation failed for user {auth_response.user.id}"
                    )
            except Exception as company_error:
                # Log the error but don't fail the registration
                print(
                    f"Warning: Company profile table not found or creation failed for user {auth_response.user.id}: {str(company_error)}"
                )

            return auth_response.dict()

        except AuthApiError as e:
            raise ValueError(f"Business registration failed: {e.message}")
        except Exception as e:
            raise ValueError(f"Business registration failed: {str(e)}")

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
            # Get user profile
            profile_response = (
                self.client.table("user_profiles")
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not profile_response.data:
                return None

            profile_data = profile_response.data

            # Get company profile if exists
            try:
                company_response = (
                    self.client.table("company_profiles")
                    .select("*")
                    .eq("user_id", user_id)
                    .single()
                    .execute()
                )
                profile_data["company"] = company_response.data
            except Exception:
                # Company profile doesn't exist, which is fine
                profile_data["company"] = None

            return profile_data

        except Exception as e:
            print(f"Error fetching user profile: {str(e)}")
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
