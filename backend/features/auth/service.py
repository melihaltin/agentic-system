# features/auth/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid

from .schemas import User, RefreshToken
from .models import UserRegister, UserLogin, UserResponse, TokenResponse, AuthResponse
from core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    decode_token
)
from core.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserRegister) -> AuthResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self._get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if user_data.username:
            existing_username = await self._get_user_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        # Generate tokens
        access_token = create_access_token(subject=db_user.id)
        refresh_token_str = create_refresh_token(subject=db_user.id)
        
        # Store refresh token
        await self._store_refresh_token(db_user.id, refresh_token_str)
        
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
        
        user_response = UserResponse.from_orm(db_user)
        
        return AuthResponse(user=user_response, tokens=tokens)

    async def login_user(self, login_data: UserLogin) -> AuthResponse:
        """Authenticate user and return tokens"""
        user = await self._get_user_by_email(login_data.email)
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Generate tokens
        access_token = create_access_token(subject=user.id)
        refresh_token_str = create_refresh_token(subject=user.id)
        
        # Store refresh token
        await self._store_refresh_token(user.id, refresh_token_str)
        
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
        
        user_response = UserResponse.from_orm(user)
        
        return AuthResponse(user=user_response, tokens=tokens)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Generate new access token using refresh token"""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token exists and is not revoked
        db_token = await self._get_refresh_token(refresh_token)
        if not db_token or db_token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked or not found"
            )
        
        # Check if refresh token is expired
        if db_token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Generate new access token
        access_token = create_access_token(subject=user_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Keep the same refresh token
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )

    async def logout_user(self, refresh_token: str) -> bool:
        """Revoke refresh token"""
        db_token = await self._get_refresh_token(refresh_token)
        if db_token:
            db_token.is_revoked = True
            await self.db.commit()
        return True

    async def get_current_user(self, token: str) -> User:
        """Get current user from access token"""
        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = await self._get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        return user

    # Private methods
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def _get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def _store_refresh_token(self, user_id: str, token: str) -> RefreshToken:
        expires_at = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
        
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        self.db.add(db_token)
        await self.db.commit()
        return db_token

    async def _get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).filter(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()