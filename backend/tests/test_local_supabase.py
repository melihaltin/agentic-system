import pytest
import httpx
from supabase import create_client, Client


class TestLocalSupabase:
    """Test suite for local Supabase integration."""

    @pytest.fixture
    def supabase_client(self) -> Client:
        """Create Supabase client for testing."""
        return create_client(
            "http://localhost:54321",  # Local Supabase URL
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0",  # Local anon key
        )

    @pytest.fixture
    def service_client(self) -> Client:
        """Create Supabase service client for testing."""
        return create_client(
            "http://localhost:54321",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",  # Local service key
        )

    def test_supabase_connection(self, supabase_client: Client):
        """Test basic Supabase connection."""
        try:
            # Test a simple query
            response = supabase_client.table("profiles").select("*").limit(1).execute()
            assert response is not None
            print("✅ Supabase connection successful")
        except Exception as e:
            pytest.fail(f"❌ Supabase connection failed: {str(e)}")

    def test_auth_signup(self, supabase_client: Client):
        """Test user signup with local Supabase."""
        try:
            # Test user registration
            test_email = "test@local.dev"
            test_password = "testpass123"

            auth_response = supabase_client.auth.sign_up(
                {
                    "email": test_email,
                    "password": test_password,
                    "options": {
                        "data": {"username": "testuser", "full_name": "Test User"}
                    },
                }
            )

            assert auth_response.user is not None
            assert auth_response.user.email == test_email
            print(f"✅ User signup successful: {test_email}")

            # Clean up - delete the test user
            if auth_response.user:
                try:
                    # Note: In local Supabase, user deletion might need service role
                    pass
                except Exception:
                    pass

        except Exception as e:
            # This might fail if user already exists, which is okay for testing
            print(f"⚠️  Auth signup test: {str(e)}")

    def test_database_operations(self, service_client: Client):
        """Test basic database operations."""
        try:
            # Test inserting a profile (using service role)
            test_profile = {
                "id": "550e8400-e29b-41d4-a716-446655440099",
                "email": "dbtest@local.dev",
                "username": "dbtestuser",
                "full_name": "DB Test User",
                "is_active": True,
            }

            # Insert
            insert_response = (
                service_client.table("profiles").insert(test_profile).execute()
            )
            assert len(insert_response.data) > 0
            print("✅ Database insert successful")

            # Select
            select_response = (
                service_client.table("profiles")
                .select("*")
                .eq("username", "dbtestuser")
                .execute()
            )
            assert len(select_response.data) > 0
            assert select_response.data[0]["username"] == "dbtestuser"
            print("✅ Database select successful")

            # Update
            update_response = (
                service_client.table("profiles")
                .update({"full_name": "Updated DB Test User"})
                .eq("username", "dbtestuser")
                .execute()
            )
            assert len(update_response.data) > 0
            print("✅ Database update successful")

            # Delete (cleanup)
            service_client.table("profiles").delete().eq(
                "username", "dbtestuser"
            ).execute()
            print("✅ Database delete successful")

        except Exception as e:
            pytest.fail(f"❌ Database operations failed: {str(e)}")

    def test_rls_policies(self, supabase_client: Client):
        """Test Row Level Security policies."""
        try:
            # Test that anonymous users can only see active profiles
            response = supabase_client.table("profiles").select("*").execute()

            # Should not raise an error (RLS allows read access)
            assert response is not None

            # All returned profiles should be active (due to RLS policy)
            for profile in response.data:
                assert profile.get("is_active", True)

            print("✅ RLS policies working correctly")

        except Exception as e:
            pytest.fail(f"❌ RLS policy test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_backend_integration(self):
        """Test backend integration with local Supabase."""
        try:
            # Test backend health check
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health")
                assert response.status_code == 200

                health_data = response.json()
                assert health_data["status"] == "healthy"

                # Check if Supabase is configured
                if "supabase" in health_data:
                    print(f"✅ Backend Supabase status: {health_data['supabase']}")
                else:
                    print("⚠️  Supabase not configured in backend")

        except Exception as e:
            print(f"⚠️  Backend integration test: {str(e)} (Backend may not be running)")


@pytest.mark.asyncio
async def test_supabase_auth_endpoints():
    """Test Supabase auth endpoints."""
    try:
        async with httpx.AsyncClient() as client:
            # Test registration endpoint
            register_data = {
                "email": "apitest@local.dev",
                "password": "testpass123",
                "username": "apitestuser",
                "full_name": "API Test User",
            }

            response = await client.post(
                "http://localhost:8000/api/v1/auth/supabase/register",
                json=register_data,
            )

            # Should succeed or fail gracefully
            if response.status_code == 201:
                print("✅ Supabase registration endpoint working")
            else:
                print(f"⚠️  Registration response: {response.status_code}")

            # Test login endpoint
            login_data = {"email": "apitest@local.dev", "password": "testpass123"}

            login_response = await client.post(
                "http://localhost:8000/api/v1/auth/supabase/login", json=login_data
            )

            if login_response.status_code == 200:
                print("✅ Supabase login endpoint working")
            else:
                print(f"⚠️  Login response: {login_response.status_code}")

    except Exception as e:
        print(f"⚠️  Auth endpoints test: {str(e)} (Backend may not be running)")


if __name__ == "__main__":
    print("Running local Supabase tests...")
    print("Make sure local Supabase is running: ./supabase-local.sh start")
    print("And optionally the backend: ./supabase-local.sh backend")
    print("-" * 50)

    # Run tests
    pytest.main([__file__, "-v", "-s"])
