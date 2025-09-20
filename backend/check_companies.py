#!/usr/bin/env python3
"""
Script to check existing company profiles in the database
"""
import os
import sys
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


def main():
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        sys.exit(1)

    supabase: Client = create_client(supabase_url, supabase_key)

    print("🔍 Checking company profiles in the database...")

    try:
        # Query all company profiles
        result = supabase.table("company_profile").select("*").execute()

        if result.data:
            print(f"\n✅ Found {len(result.data)} company profile(s):")
            for company in result.data:
                print(f"  - ID: {company.get('id')}")
                print(f"    Name: {company.get('company_name', 'N/A')}")
                print(f"    User ID: {company.get('user_id', 'N/A')}")
                print(f"    Created: {company.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ No company profiles found in the database")

        # Also check if there are any user profiles
        print("🔍 Checking user profiles (auth.users equivalent)...")
        users_result = supabase.table("user_profile").select("*").execute()

        if users_result.data:
            print(f"\n✅ Found {len(users_result.data)} user profile(s):")
            for user in users_result.data:
                print(f"  - ID: {user.get('id')}")
                print(f"    Email: {user.get('email', 'N/A')}")
                print(f"    Created: {user.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ No user profiles found")

    except Exception as e:
        print(f"❌ Error querying database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
