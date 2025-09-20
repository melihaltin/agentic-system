from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ElevenLabs
    elevenlabs_api_key: str

    # App
    app_name: str = "IQRA"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
