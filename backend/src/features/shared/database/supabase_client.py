from supabase import create_client, Client
from src.core.config import settings


def get_supabase_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase_anon_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_anon_key)


# Singleton instances
supabase: Client = get_supabase_client()
supabase_anon: Client = get_supabase_anon_client()
