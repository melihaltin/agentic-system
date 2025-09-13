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
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Supabase (Optional)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # CORS
    allowed_hosts: str = "*"
    allowed_origins: str = "*"
    
    def get_allowed_hosts(self) -> list:
        """Parse allowed_hosts string into a list"""
        if isinstance(self.allowed_hosts, str):
            if self.allowed_hosts == "*":
                return ["*"]
            return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]
        return self.allowed_hosts
    
    def get_allowed_origins(self) -> list:
        """Parse allowed_origins string into a list"""
        if isinstance(self.allowed_origins, str):
            if self.allowed_origins == "*":
                return ["*"]
            return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        return self.allowed_origins
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        extra = "ignore"
        case_sensitive = False

settings = Settings()