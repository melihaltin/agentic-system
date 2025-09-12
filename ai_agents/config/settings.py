"""
Application settings and configuration.
"""

import os
from typing import Optional
from datetime import datetime
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # Twilio Configuration
    twilio_account_sid: Optional[str] = Field(None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(None, env="TWILIO_PHONE_NUMBER")

    # Database Configuration
    database_url: str = Field("sqlite:///./ai_agents.db", env="DATABASE_URL")

    # Application Settings
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")

    # Agent Configuration
    max_iterations: int = Field(10, env="MAX_ITERATIONS")
    timeout_seconds: int = Field(300, env="TIMEOUT_SECONDS")

    # Properties with uppercase for backward compatibility
    @property
    def OPENAI_API_KEY(self) -> str:
        return self.openai_api_key

    @property
    def TWILIO_ACCOUNT_SID(self) -> Optional[str]:
        return self.twilio_account_sid

    @property
    def TWILIO_AUTH_TOKEN(self) -> Optional[str]:
        return self.twilio_auth_token

    @property
    def TWILIO_PHONE_NUMBER(self) -> Optional[str]:
        return self.twilio_phone_number

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def DEBUG(self) -> bool:
        return self.debug

    @property
    def LOG_LEVEL(self) -> str:
        return self.log_level

    @property
    def HOST(self) -> str:
        return self.host

    @property
    def PORT(self) -> int:
        return self.port

    @property
    def MAX_ITERATIONS(self) -> int:
        return self.max_iterations

    @property
    def TIMEOUT_SECONDS(self) -> int:
        return self.timeout_seconds

    def get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.now().isoformat()

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
