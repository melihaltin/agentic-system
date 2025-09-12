from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from features.users.repository import UserRepository
from features.users.service import UserService


async def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    """Get user repository dependency."""
    return UserRepository(db)


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Get user service dependency."""
    return UserService(user_repository)
