from fastapi import HTTPException, status
from features.users.repository import UserRepository
from features.users.models import UserCreate, UserResponse
from features.auth.models import LoginRequest, TokenResponse
from features.users.schemas import User
from core.security import verify_password, create_access_token
from core.config import settings
from datetime import timedelta
import structlog

logger = structlog.get_logger()


class AuthService:
    """Service layer for authentication operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user with email and password."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            logger.warning(f"Authentication failed - user not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Authentication failed - inactive user: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed - incorrect password: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"User authenticated successfully: {email}")
        return user

    async def login(self, login_data: LoginRequest) -> TokenResponse:
        """Login user and return access token."""
        user = await self.authenticate_user(login_data.email, login_data.password)

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def register(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        existing_username = await self.user_repository.get_by_username(
            user_data.username
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists",
            )

        try:
            user = await self.user_repository.create(user_data)
            logger.info(f"New user registered: {user.email}")
            return UserResponse.model_validate(user)

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email for token validation."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user account"
            )

        return user
