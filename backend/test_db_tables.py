"""
Simple test for database tables and agent data
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import supabase


async def test_database_tables():
    """Test which tables exist and have data"""

    print("🔍 Testing database tables...")
    print("=" * 50)

    # Test company_agents table
    try:
        response = supabase.table("company_agents").select("*").limit(5).execute()
        print(f"✅ company_agents table: {len(response.data)} records found")
        if response.data:
            print("   Sample record keys:", list(response.data[0].keys()))
    except Exception as e:
        print(f"❌ company_agents table error: {str(e)}")

    # Test company_profile table
    try:
        response = supabase.table("company_profile").select("*").limit(5).execute()
        print(f"✅ company_profile table: {len(response.data)} records found")
        if response.data:
            print("   Sample record keys:", list(response.data[0].keys()))
    except Exception as e:
        print(f"❌ company_profile table error: {str(e)}")

    # Test agent_templates table
    try:
        response = supabase.table("agent_templates").select("*").limit(5).execute()
        print(f"✅ agent_templates table: {len(response.data)} records found")
        if response.data:
            print("   Sample record keys:", list(response.data[0].keys()))
    except Exception as e:
        print(f"❌ agent_templates table error: {str(e)}")

    # Test agent_integration_links table
    try:
        response = (
            supabase.table("agent_integration_links").select("*").limit(5).execute()
        )
        print(f"✅ agent_integration_links table: {len(response.data)} records found")
        if response.data:
            print("   Sample record keys:", list(response.data[0].keys()))
    except Exception as e:
        print(f"❌ agent_integration_links table error: {str(e)}")

    # Test company_integration_configurations table
    try:
        response = (
            supabase.table("company_integration_configurations")
            .select("*")
            .limit(5)
            .execute()
        )
        print(
            f"✅ company_integration_configurations table: {len(response.data)} records found"
        )
        if response.data:
            print("   Sample record keys:", list(response.data[0].keys()))
    except Exception as e:
        print(f"❌ company_integration_configurations table error: {str(e)}")

    # Test integration_providers table
    try:
        response = (
            supabase.table("integration_providers").select("*").limit(5).execute()
        )
        print(f"✅ integration_providers table: {len(response.data)} records found")
        if response.data:
            print("   Sample record keys:", list(response.data[0].keys()))
    except Exception as e:
        print(f"❌ integration_providers table error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_database_tables())
