# core/config.py
from pydantic_settings import BaseSettings
from pydantic import field_validator, computed_field
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    app_name: str = "FastAPI Auth App"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: str
    
    @computed_field
    @property
    def database_url_sync(self) -> str:
        """Generate synchronous database URL from async URL"""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Supabase (Optional)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # CORS
    allowed_hosts: list = ["*"]
    allowed_origins: list = ["*"]
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        extra = "ignore"
        case_sensitive = False

settings = Settings()