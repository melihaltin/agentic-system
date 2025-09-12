from supabase import Client
from features.users.models import UserCreate, UserUpdate
from typing import Optional, List, Dict, Any
import structlog

logger = structlog.get_logger()


class SupabaseUserRepository:
    """Repository for User operations using Supabase."""
    
    def __init__(self, client: Client, service_client: Client):
        self.client = client
        self.service_client = service_client
    
    async def create_profile(self, user_id: str, user_data: UserCreate) -> Dict[str, Any]:
        """Create user profile in Supabase profiles table."""
        try:
            profile_data = {
                "id": user_id,
                "email": user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name,
                "bio": user_data.bio,
                "avatar_url": user_data.avatar_url,
                "is_active": True
            }
            
            response = self.service_client.table('profiles').insert(profile_data).execute()
            
            if response.data:
                logger.info(f"Profile created for user: {user_data.email}")
                return response.data[0]
            else:
                raise ValueError("Failed to create user profile")
                
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}")
            raise ValueError(f"Failed to create profile: {str(e)}")
    
    async def get_profile_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID."""
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching profile by ID: {str(e)}")
            return None
    
    async def get_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user profile by email."""
        try:
            response = self.client.table('profiles').select('*').eq('email', email).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching profile by email: {str(e)}")
            return None
    
    async def get_profile_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user profile by username."""
        try:
            response = self.client.table('profiles').select('*').eq('username', username).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching profile by username: {str(e)}")
            return None
    
    async def get_all_profiles(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all user profiles with pagination."""
        try:
            query = self.client.table('profiles').select('*')
            
            if active_only:
                query = query.eq('is_active', True)
            
            query = query.range(skip, skip + limit - 1).order('created_at', desc=True)
            
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error fetching profiles: {str(e)}")
            return []
    
    async def count_profiles(self, active_only: bool = True) -> int:
        """Count total user profiles."""
        try:
            query = self.client.table('profiles').select('id', count='exact')
            
            if active_only:
                query = query.eq('is_active', True)
            
            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
            
        except Exception as e:
            logger.error(f"Error counting profiles: {str(e)}")
            return 0
    
    async def update_profile(self, user_id: str, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
        """Update user profile."""
        try:
            update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
            
            if not update_data:
                return None
            
            response = self.service_client.table('profiles').update(update_data).eq('id', user_id).execute()
            
            if response.data:
                logger.info(f"Profile updated for user: {user_id}")
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            raise ValueError(f"Failed to update profile: {str(e)}")
    
    async def deactivate_profile(self, user_id: str) -> bool:
        """Deactivate user profile (soft delete)."""
        try:
            response = self.service_client.table('profiles').update({
                'is_active': False
            }).eq('id', user_id).execute()
            
            if response.data:
                logger.info(f"Profile deactivated for user: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deactivating profile: {str(e)}")
            return False
    
    async def activate_profile(self, user_id: str) -> bool:
        """Activate user profile."""
        try:
            response = self.service_client.table('profiles').update({
                'is_active': True
            }).eq('id', user_id).execute()
            
            if response.data:
                logger.info(f"Profile activated for user: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error activating profile: {str(e)}")
            return False
    
    async def search_profiles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search user profiles by username or full name."""
        try:
            # Supabase supports text search and ilike operations
            response = self.client.table('profiles').select('*').or_(
                f'username.ilike.%{query}%,full_name.ilike.%{query}%'
            ).eq('is_active', True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error searching profiles: {str(e)}")
            return []


class SupabaseStorageService:
    """Service for Supabase Storage operations."""
    
    def __init__(self, client: Client):
        self.client = client
        self.bucket_name = "avatars"  # Default bucket for user avatars
    
    async def upload_avatar(self, user_id: str, file_data: bytes, file_name: str) -> Optional[str]:
        """Upload user avatar to Supabase Storage."""
        try:
            file_path = f"{user_id}/{file_name}"
            
            # Upload file to storage
            response = self.client.storage.from_(self.bucket_name).upload(
                file_path, 
                file_data,
                file_options={"content-type": "image/*"}
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
                logger.info(f"Avatar uploaded for user {user_id}: {file_path}")
                return public_url
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error uploading avatar: {str(e)}")
            return None
    
    async def delete_avatar(self, user_id: str, file_name: str) -> bool:
        """Delete user avatar from Supabase Storage."""
        try:
            file_path = f"{user_id}/{file_name}"
            
            response = self.client.storage.from_(self.bucket_name).remove([file_path])
            
            if response:
                logger.info(f"Avatar deleted for user {user_id}: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting avatar: {str(e)}")
            return False
    
    async def list_user_files(self, user_id: str) -> List[Dict[str, Any]]:
        """List all files for a user."""
        try:
            response = self.client.storage.from_(self.bucket_name).list(user_id)
            return response if response else []
            
        except Exception as e:
            logger.error(f"Error listing user files: {str(e)}")
            return []
