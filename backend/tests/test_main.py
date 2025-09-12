import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "postgresql"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Team AI Backend API"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User",
        }
        response = await client.post("/api/v1/auth/register", json=user_data)
        # Note: This will fail without proper database setup
        # This is just to demonstrate the test structure


@pytest.mark.asyncio
async def test_login_user():
    """Test user login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_data = {"email": "test@example.com", "password": "testpassword123"}
        response = await client.post("/api/v1/auth/login", json=login_data)
        # Note: This will fail without proper database setup and existing user
        # This is just to demonstrate the test structure
