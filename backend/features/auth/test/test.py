# tests/test_auth.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, Mock
from features.auth.service import AuthService
from features.auth.models import UserRegister, UserLogin
from main import app

@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == "test@example.com"
        assert "access_token" in data["tokens"]

@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with duplicate email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword123"
            }
        )
        
        # Duplicate registration
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success():
    """Test successful login"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "testpassword123"
            }
        )
        
        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]

@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_current_user():
    """Test getting current user with valid token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "currentuser@example.com",
                "password": "testpassword123"
            }
        )
        
        token = login_response.json()["tokens"]["access_token"]
        
        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "currentuser@example.com"

@pytest.mark.asyncio
async def test_protected_route_without_token():
    """Test accessing protected route without token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No Authorization header

@pytest.mark.asyncio
async def test_protected_route_with_invalid_token():
    """Test accessing protected route with invalid token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_token():
    """Test token refresh functionality"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "testpassword123"
            }
        )
        
        refresh_token = login_response.json()["tokens"]["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

@pytest.mark.asyncio
async def test_logout():
    """Test user logout"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        login_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "logout@example.com",
                "password": "testpassword123"
            }
        )
        
        refresh_token = login_response.json()["tokens"]["refresh_token"]
        
        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

# Unit Tests for AuthService
class TestAuthService:
    def setup_method(self):
        self.mock_db = AsyncMock(spec=AsyncSession)
        self.auth_service = AuthService(self.mock_db)

    @pytest.mark.asyncio
    async def test_register_user_success(self):
        """Unit test for successful user registration"""
        # Mock database responses
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = None  # No existing user
        self.mock_db.add = AsyncMock()
        self.mock_db.commit = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        user_data = UserRegister(
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        
        # Test would continue with proper mocking...
        # This is a simplified version

# Integration Tests
class TestAuthIntegration:
    @pytest.mark.asyncio
    async def test_complete_auth_flow(self):
        """Test complete authentication flow"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. Register
            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "flow@example.com",
                    "password": "testpassword123",
                    "full_name": "Flow Test"
                }
            )
            assert register_response.status_code == 200
            
            # 2. Login
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "flow@example.com",
                    "password": "testpassword123"
                }
            )
            assert login_response.status_code == 200
            
            tokens = login_response.json()["tokens"]
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            
            # 3. Access protected route
            protected_response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert protected_response.status_code == 200
            
            # 4. Refresh token
            refresh_response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            assert refresh_response.status_code == 200
            
            # 5. Logout
            logout_response = await client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": refresh_token}
            )
            assert logout_response.status_code == 200

# Conftest.py for test setup
# conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.database import Base, get_db
from main import app
import os

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/fastapi_auth_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create test database session"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
async def client(test_session):
    """Create test client with test database"""
    def get_test_db():
        return test_session
    
    app.dependency_overrides[get_db] = get_test_db
    
    yield app
    
    app.dependency_overrides.clear()