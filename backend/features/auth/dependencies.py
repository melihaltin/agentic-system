from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from features.users.repository import UserRepository
from features.auth.service import AuthService


async def get_auth_service(db: AsyncSession = Depends(get_db_session)) -> AuthService:
    """Get auth service dependency."""
    user_repository = UserRepository(db)
    return AuthService(user_repository)
