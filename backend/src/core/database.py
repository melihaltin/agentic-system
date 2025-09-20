from supabase import create_client, Client
from src.core.config import settings


def get_supabase_client() -> Client:
    """Get Supabase client instance"""

    print("🔑 Initializing Supabase client...")

    print(f"🌐 Supabase URL: {settings.supabase_url}")
    return create_client(
        supabase_url=settings.supabase_url, supabase_key=settings.supabase_service_key
    )


# Global client instance
supabase: Client = get_supabase_client()
