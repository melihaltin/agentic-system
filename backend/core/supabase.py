from supabase import create_client, Client
from core.config import settings
import structlog

logger = structlog.get_logger()


class SupabaseClient:
    """Supabase client wrapper for database and authentication operations."""
    
    def __init__(self):
        self._client: Client = None
        self._service_client: Client = None
    
    @property
    def client(self) -> Client:
        """Get Supabase client with anon key (for public operations)."""
        if self._client is None:
            try:
                self._client = create_client(
                    settings.supabase_url, 
                    settings.supabase_anon_key
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise
        return self._client
    
    @property
    def service_client(self) -> Client:
        """Get Supabase client with service role key (for admin operations)."""
        if self._service_client is None:
            try:
                self._service_client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_key
                )
                logger.info("Supabase service client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase service client: {str(e)}")
                raise
        return self._service_client
    
    async def test_connection(self) -> bool:
        """Test Supabase connection."""
        try:
            # Try to perform a simple query to test connection
            self.client.table('users').select('*').limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False


# Create global Supabase client instance
supabase_client = SupabaseClient()


def get_supabase_client() -> Client:
    """Get Supabase client dependency."""
    return supabase_client.client


def get_supabase_service_client() -> Client:
    """Get Supabase service client dependency."""
    return supabase_client.service_client
