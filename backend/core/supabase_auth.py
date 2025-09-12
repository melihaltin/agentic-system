from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from core.supabase import get_supabase_client, get_supabase_service_client
from features.users.models import UserCreate
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()

security = HTTPBearer()


class SupabaseAuthService:
    """Service for Supabase authentication operations."""
    
    def __init__(self, client: Client, service_client: Client):
        self.client = client
        self.service_client = service_client
    
    async def sign_up_with_email(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user with Supabase Auth."""
        try:
            # Create user with Supabase Auth
            auth_response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "username": user_data.username,
                        "full_name": user_data.full_name,
                        "bio": user_data.bio,
                        "avatar_url": user_data.avatar_url
                    }
                }
            })
            
            if auth_response.user:
                logger.info(f"User created with Supabase Auth: {user_data.email}")
                
                # Insert additional user data into profiles table
                profile_data = {
                    "id": auth_response.user.id,
                    "username": user_data.username,
                    "full_name": user_data.full_name,
                    "bio": user_data.bio,
                    "avatar_url": user_data.avatar_url,
                    "email": user_data.email
                }
                
                self.service_client.table('profiles').insert(profile_data).execute()
                
                return {
                    "user": auth_response.user,
                    "session": auth_response.session,
                    "message": "User created successfully. Please check your email for verification."
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
                
        except Exception as e:
            logger.error(f"Supabase sign up error: {str(e)}")
            if "already registered" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def sign_in_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user with email and password."""
        try:
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user and auth_response.session:
                logger.info(f"User signed in with Supabase Auth: {email}")
                return {
                    "user": auth_response.user,
                    "session": auth_response.session,
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
                
        except Exception as e:
            logger.error(f"Supabase sign in error: {str(e)}")
            if "Invalid login credentials" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
    
    async def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Supabase JWT token."""
        try:
            # Set the session with the provided token
            self.client.auth.set_session(token, "")
            
            # Get current user
            user_response = self.client.auth.get_user(token)
            
            if user_response.user:
                # Get additional profile data
                profile_response = self.client.table('profiles').select('*').eq('id', user_response.user.id).single().execute()
                
                return {
                    "auth_user": user_response.user,
                    "profile": profile_response.data if profile_response.data else None
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user from token: {str(e)}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        try:
            auth_response = self.client.auth.refresh_session(refresh_token)
            
            if auth_response.session:
                return {
                    "session": auth_response.session,
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
    
    async def sign_out(self, token: str) -> Dict[str, str]:
        """Sign out user by invalidating token."""
        try:
            self.client.auth.set_session(token, "")
            self.client.auth.sign_out()
            
            logger.info("User signed out successfully")
            return {"message": "Successfully signed out"}
            
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return {"message": "Sign out completed"}
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile in Supabase."""
        try:
            # Update profile table
            response = self.service_client.table('profiles').update(profile_data).eq('id', user_id).execute()
            
            if response.data:
                logger.info(f"Profile updated for user: {user_id}")
                return response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
                
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )


async def get_supabase_auth_service(
    client: Client = Depends(get_supabase_client),
    service_client: Client = Depends(get_supabase_service_client)
) -> SupabaseAuthService:
    """Get Supabase auth service dependency."""
    return SupabaseAuthService(client, service_client)


async def get_current_supabase_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_supabase_auth_service)
) -> Dict[str, Any]:
    """Get current user from Supabase JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = await auth_service.get_user_from_token(credentials.credentials)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


async def get_optional_supabase_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: SupabaseAuthService = Depends(get_supabase_auth_service)
) -> Optional[Dict[str, Any]]:
    """Get current user from Supabase JWT token (optional)."""
    if not credentials:
        return None
    
    try:
        return await auth_service.get_user_from_token(credentials.credentials)
    except Exception:
        return None
