from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from features.users.schemas import User
from features.users.models import UserCreate, UserUpdate
from core.security import get_password_hash
from typing import Optional, List
import structlog

logger = structlog.get_logger()


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        try:
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                bio=user_data.bio,
                avatar_url=user_data.avatar_url,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=False,
            )

            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)

            logger.info(f"User created successfully: {user_data.email}")
            return db_user

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Failed to create user due to integrity error: {str(e)}")
            raise ValueError("User with this email or username already exists")

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[User]:
        """Get all users with pagination."""
        query = select(User)

        if active_only:
            query = query.where(User.is_active.is_(True))

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_all(self, active_only: bool = True) -> int:
        """Count total users."""
        query = select(func.count(User.id))

        if active_only:
            query = query.where(User.is_active.is_(True))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user by ID."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_user, field, value)

        try:
            await self.db.commit()
            await self.db.refresh(db_user)

            logger.info(f"User updated successfully: {db_user.email}")
            return db_user

        except IntegrityError:
            await self.db.rollback()
            logger.error("Failed to update user due to integrity error")
            raise ValueError("User with this email or username already exists")

    async def delete(self, user_id: int) -> bool:
        """Soft delete user by setting is_active to False."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False

        db_user.is_active = False
        await self.db.commit()

        logger.info(f"User deactivated successfully: {db_user.email}")
        return True

    async def activate(self, user_id: int) -> bool:
        """Activate user by setting is_active to True."""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False

        db_user.is_active = True
        await self.db.commit()

        logger.info(f"User activated successfully: {db_user.email}")
        return True
