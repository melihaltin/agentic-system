#!/usr/bin/env python3
"""
Test script for voices API
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables for testing (replace with your actual values)
os.environ.setdefault("SUPABASE_URL", "https://xhtjtfxlyszfxvhwcemx.supabase.co")
os.environ.setdefault(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhodGp0ZnhseXN6Znh2aHdjZW14Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc2NjQwNzksImV4cCI6MjA3MzI0MDA3OX0.rk3mPXQ-UTq0vP2dLZ5Kjfik6WvBOysAd3JDjFW5Iuo",
)
os.environ.setdefault(
    "SUPABASE_SERVICE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhodGp0ZnhseXN6Znh2aHdjZW14Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzY2NDA3OSwiZXhwIjoyMDczMjQwMDc5fQ.70srrl2oW1n7UMQ3l_Bg0l0UaXvZalPciX-PeykoPfU",
)
os.environ.setdefault("JWT_SECRET", "your_jwt_secret")
os.environ.setdefault(
    "ELEVENLABS_API_KEY", "sk_fabb6806b7e2cfa72ba43b744191101c191ba9c7bc1d95d1"
)


async def test_elevenlabs_service():
    """Test ElevenLabs service functionality"""
    try:
        from src.features.agents.service import elevenlabs_service

        print("🔄 Testing ElevenLabs API connection...")

        # Test fetching voices from ElevenLabs
        voices = await elevenlabs_service.fetch_voices_from_elevenlabs()
        print(f"✅ Successfully fetched {len(voices)} voices from ElevenLabs")

        # Print first few voices for inspection
        for i, voice in enumerate(voices[:3]):
            print(f"Voice {i+1}: {voice.name} (ID: {voice.voice_id})")

        print("\n🔄 Testing database sync...")

        # Test syncing to database
        sync_result = await elevenlabs_service.sync_voices_from_elevenlabs()
        print(f"✅ Sync completed:")
        print(f"   - Synced: {sync_result.synced_count}")
        print(f"   - Skipped: {sync_result.skipped_count}")
        print(f"   - Errors: {len(sync_result.errors)}")

        if sync_result.errors:
            for error in sync_result.errors:
                print(f"   ❌ {error}")

        print("\n🔄 Testing database retrieval...")

        # Test getting voices from database
        db_voices = await elevenlabs_service.get_voices_from_database()
        print(f"✅ Retrieved {len(db_voices)} voices from database")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Starting Voices API Test\n")

    success = await test_elevenlabs_service()

    if success:
        print("\n✅ All tests passed!")
        print("\nAPI Endpoints available:")
        print("- POST /v1/voices/sync - Sync voices from ElevenLabs")
        print("- GET /v1/voices/ - Get voices from database")
        print(
            "- GET /v1/voices/providers/elevenlabs - Get voices directly from ElevenLabs"
        )

        print("\nExample usage:")
        print("curl -X POST http://localhost:8000/v1/voices/sync")
        print("curl http://localhost:8000/v1/voices/")
    else:
        print("\n❌ Tests failed!")
        print("\nMake sure to:")
        print("1. Create a .env file with your API keys")
        print("2. Run the migration script to create database tables")
        print("3. Verify your ElevenLabs API key is valid")


if __name__ == "__main__":
    asyncio.run(main())
