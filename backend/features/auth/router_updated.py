from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str = None
    is_active: bool = True

@router.get("/")
async def auth_root():
    """Auth root endpoint."""
    return {"message": "Authentication API"}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """Register a new user."""
    # Placeholder implementation
    if user_data.email == "test@example.com":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Simulate user creation
    return UserResponse(
        id="123e4567-e89b-12d3-a456-426614174000",
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True
    )

@router.post("/login")
async def login(login_data: LoginRequest):
    """Login endpoint."""
    # Placeholder implementation
    if login_data.email == "test@example.com" and login_data.password == "password":
        return {
            "access_token": "fake-jwt-token",
            "token_type": "bearer",
            "expires_in": 1800
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )

@router.post("/logout")
async def logout():
    """Logout endpoint."""
    return {"message": "Successfully logged out"}