from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request model."""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""

    token: str = Field(..., description="Reset token")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )


class EmailVerificationRequest(BaseModel):
    """Email verification request model."""

    token: str = Field(..., description="Verification token")
