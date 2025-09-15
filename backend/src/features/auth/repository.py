from supabase import Client
from gotrue.errors import AuthApiError
from typing import Optional, Dict, Any
from .schemas import (
    RegisterRequest,
    BusinessRegistrationRequest,
    LoginRequest,
    ProfileUpdateRequest,
)
from ..shared.database.supabase_client import supabase, get_supabase_client


class AuthRepository:
    def __init__(self, client: Client = supabase):
        self.client = client
        # Service role client for admin operations
        self.admin_client = get_supabase_client()

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
            # Use admin client with service role for user creation without email confirmation
            admin_response = self.admin_client.auth.admin.create_user(
                {
                    "email": request.email,
                    "password": request.password,
                    "user_metadata": {"full_name": request.full_name},
                    "email_confirm": True,  # Admin API can set user as confirmed
                }
            )
            print(f"DEBUG: Admin response: {admin_response}")

            if not admin_response.user:
                print("DEBUG: No user in admin response")
                raise ValueError("User creation failed")

            # Since admin API doesn't return session, we need to sign in the user
            auth_response = self.client.auth.sign_in_with_password(
                {"email": request.email, "password": request.password}
            )

            if not auth_response.user:
                raise ValueError("User creation failed")

            # Create company profile using admin client
            company_data = {
                "user_id": auth_response.user.id,
                "company_name": request.company_name,
                "phone_number": request.phone_number,
                "business_category": request.business_category,
            }

            try:
                company_response = (
                    self.admin_client.table("company_profiles")
                    .insert(company_data)
                    .execute()
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
            # Get company profile (this is our main profile table)
            company_response = (
                self.client.table("company_profiles")
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            if not company_response.data:
                return None

            profile_data = company_response.data

            # Get user info from Supabase auth using admin client
            try:
                user_info = self.admin_client.auth.admin.get_user_by_id(user_id)
                if user_info and user_info.user:
                    profile_data["email"] = user_info.user.email
                    profile_data["full_name"] = user_info.user.user_metadata.get(
                        "full_name", ""
                    )
            except Exception as e:
                print(f"Warning: Could not fetch user auth info: {e}")

            # Structure the response to match expected format
            return {
                "id": user_id,
                "email": profile_data.get("email", ""),
                "full_name": profile_data.get("full_name", ""),
                "company": {
                    "company_name": profile_data.get("company_name", ""),
                    "phone_number": profile_data.get("phone_number", ""),
                    "business_category": profile_data.get("business_category", ""),
                    "address": profile_data.get("address", ""),
                    "website": profile_data.get("website", ""),
                    "timezone": profile_data.get("timezone", "America/New_York"),
                },
            }

        except Exception as e:
            print(f"Error fetching user profile: {str(e)}")
            return None

    async def update_user_profile(
        self, user_id: str, request: ProfileUpdateRequest
    ) -> Dict[str, Any]:
        try:
            update_data = request.dict(exclude_unset=True)

            # All profile data goes to company_profiles table
            # Only include fields that exist in the current schema
            company_fields = {
                k: v
                for k, v in update_data.items()
                if k
                in [
                    "company_name",
                    "phone_number",
                    "business_category",
                    "address",
                    "website",
                    "timezone",
                ]
            }

            # Update user metadata in Supabase auth if full_name is provided using admin client
            if "full_name" in update_data:
                try:
                    self.admin_client.auth.admin.update_user_by_id(
                        user_id,
                        {"user_metadata": {"full_name": update_data["full_name"]}},
                    )
                except Exception as e:
                    print(f"Warning: Could not update user metadata: {e}")

            # Update company profile if there are company fields
            if company_fields:
                company_fields["updated_at"] = "NOW()"
                (
                    self.client.table("company_profiles")
                    .update(company_fields)
                    .eq("user_id", user_id)
                    .execute()
                )

            # Return updated profile
            return await self.get_user_profile(user_id)
        except Exception as e:
            raise ValueError(f"Profile update failed: {str(e)}")

    async def change_password(self, access_token: str, new_password: str) -> bool:
        try:
            self.client.auth.update_user({"password": new_password}, access_token)
            return True
        except AuthApiError:
            return False
