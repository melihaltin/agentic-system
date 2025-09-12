from fastapi import HTTPException, status, Depends
from features.users.models import UserCreate, UserUpdate, UserResponse, UserListResponse
from features.users.service import UserService
from core.supabase_auth import SupabaseAuthService, get_supabase_auth_service
from core.supabase_repository import SupabaseUserRepository
from core.supabase import get_supabase_client, get_supabase_service_client
from core.config import settings
from supabase import Client
from typing import Union, Dict, Any
import structlog

logger = structlog.get_logger()


class HybridUserService:
    """
    Hybrid user service that can work with both traditional PostgreSQL
    and Supabase based on configuration.
    """
    
    def __init__(
        self, 
        traditional_service: UserService = None,
        supabase_auth_service: SupabaseAuthService = None,
        supabase_user_repository: SupabaseUserRepository = None
    ):
        self.use_supabase = settings.use_supabase_auth
        self.traditional_service = traditional_service
        self.supabase_auth_service = supabase_auth_service
        self.supabase_user_repository = supabase_user_repository
    
    async def create_user(self, user_data: UserCreate) -> Union[UserResponse, Dict[str, Any]]:
        """Create user using the configured backend."""
        if self.use_supabase and self.supabase_auth_service:
            # Use Supabase Auth for user creation
            return await self.supabase_auth_service.sign_up_with_email(user_data)
        else:
            # Use traditional PostgreSQL
            if not self.traditional_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Traditional user service not available"
                )
            return await self.traditional_service.create_user(user_data)
    
    async def authenticate_user(self, email: str, password: str) -> Union[UserResponse, Dict[str, Any]]:
        """Authenticate user using the configured backend."""
        if self.use_supabase and self.supabase_auth_service:
            # Use Supabase Auth
            return await self.supabase_auth_service.sign_in_with_email(email, password)
        else:
            # Use traditional authentication
            if not self.traditional_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Traditional auth service not available"
                )
            # Note: Traditional service doesn't have authenticate_user method,
            # this would need to be implemented in the auth service
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Traditional authentication not implemented in this method"
            )
    
    async def get_user_profile(self, user_identifier: str) -> Union[UserResponse, Dict[str, Any]]:
        """Get user profile using the configured backend."""
        if self.use_supabase and self.supabase_user_repository:
            # Try to get by ID first (Supabase uses UUID), then by username
            if len(user_identifier) == 36:  # UUID length
                profile = await self.supabase_user_repository.get_profile_by_id(user_identifier)
            else:
                profile = await self.supabase_user_repository.get_profile_by_username(user_identifier)
            
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return profile
        else:
            # Use traditional service
            if not self.traditional_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Traditional user service not available"
                )
            
            try:
                user_id = int(user_identifier)
                return await self.traditional_service.get_user_by_id(user_id)
            except ValueError:
                return await self.traditional_service.get_user_by_username(user_identifier)
    
    async def update_user_profile(
        self, 
        user_identifier: str, 
        user_data: UserUpdate,
        current_user: Union[Any, Dict[str, Any]] = None
    ) -> Union[UserResponse, Dict[str, Any]]:
        """Update user profile using the configured backend."""
        if self.use_supabase and self.supabase_user_repository:
            # Use Supabase
            updated_profile = await self.supabase_user_repository.update_profile(
                user_identifier, 
                user_data
            )
            
            if not updated_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return updated_profile
        else:
            # Use traditional service
            if not self.traditional_service or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Traditional user service or current user not available"
                )
            
            user_id = int(user_identifier)
            return await self.traditional_service.update_user(user_id, user_data, current_user)
    
    async def get_users_list(
        self, 
        page: int = 1, 
        per_page: int = 20
    ) -> Union[UserListResponse, Dict[str, Any]]:
        """Get paginated users list using the configured backend."""
        if self.use_supabase and self.supabase_user_repository:
            # Use Supabase
            skip = (page - 1) * per_page
            profiles = await self.supabase_user_repository.get_all_profiles(
                skip=skip, 
                limit=per_page,
                active_only=True
            )
            total = await self.supabase_user_repository.count_profiles(active_only=True)
            
            has_next = (skip + per_page) < total
            has_prev = page > 1
            
            return {
                "users": profiles,
                "total": total,
                "page": page,
                "per_page": per_page,
                "has_next": has_next,
                "has_prev": has_prev
            }
        else:
            # Use traditional service
            if not self.traditional_service:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Traditional user service not available"
                )
            return await self.traditional_service.get_users(page=page, per_page=per_page)
    
    async def search_users(self, query: str, limit: int = 20) -> Union[list, Dict[str, Any]]:
        """Search users using the configured backend."""
        if self.use_supabase and self.supabase_user_repository:
            # Use Supabase
            return await self.supabase_user_repository.search_profiles(query, limit)
        else:
            # For traditional service, this would need to be implemented
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Search not implemented for traditional backend"
            )


async def get_hybrid_user_service(
    traditional_service: UserService = Depends(lambda: None),
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
    client: Client = Depends(get_supabase_client),
    service_client: Client = Depends(get_supabase_service_client)
) -> HybridUserService:
    """Get hybrid user service dependency."""
    supabase_user_repository = SupabaseUserRepository(client, service_client)
    
    return HybridUserService(
        traditional_service=traditional_service,
        supabase_auth_service=supabase_auth_service,
        supabase_user_repository=supabase_user_repository
    )
