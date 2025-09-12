from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Environment
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=True, description="Debug mode")

    # API Configuration
    api_title: str = Field(default="Team AI Backend API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")

    # Security
    secret_key: str = Field(..., description="Secret key for JWT encoding")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )

    # Database Configuration
    postgres_server: str = Field(
        default="localhost", description="PostgreSQL server host"
    )
    postgres_port: int = Field(default=5432, description="PostgreSQL server port")
    postgres_user: str = Field(..., description="PostgreSQL username")
    postgres_password: str = Field(..., description="PostgreSQL password")
    postgres_db: str = Field(..., description="PostgreSQL database name")

    @computed_field
    @property
    def database_url(self) -> str:
        """Async PostgreSQL database URL."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

    @computed_field
    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL database URL (for Alembic migrations)."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

    # CORS Configuration
    allowed_hosts: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ],
        description="Allowed hosts for CORS",
    )

    # Redis Configuration (optional for caching)
    redis_url: str = Field(
        default="redis://localhost:6379", description="Redis URL for caching"
    )

    # File Upload Configuration
    max_file_size: int = Field(
        default=10 * 1024 * 1024, description="Maximum file size in bytes (10MB)"
    )
    upload_path: str = Field(default="uploads", description="Upload directory path")

    # Pagination
    default_page_size: int = Field(
        default=20, description="Default pagination page size"
    )
    max_page_size: int = Field(default=100, description="Maximum pagination page size")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Create settings instance
settings = Settings()
