from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from core.database import get_db_session
from core.config import settings
from features.users.repository import UserRepository
from features.users.schemas import User
from typing import Optional
import structlog

logger = structlog.get_logger()

# JWT token security scheme
security = HTTPBearer()


async def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    """Get user repository dependency."""
    return UserRepository(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

    except JWTError:
        logger.warning("Invalid JWT token provided")
        raise credentials_exception

    user = await user_repository.get_by_email(email)
    if user is None:
        logger.warning(f"User not found for email: {email}")
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (not disabled)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_repository: UserRepository = Depends(get_user_repository),
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None."""
    if not credentials:
        return None

    try:
        return get_current_user(credentials, user_repository)
    except HTTPException:
        return None
