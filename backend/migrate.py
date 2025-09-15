#!/usr/bin/env python3

import os
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(url, service_key)

# Add missing columns to company_profiles table
sql = """
ALTER TABLE public.company_profiles 
ADD COLUMN IF NOT EXISTS address text,
ADD COLUMN IF NOT EXISTS website text,
ADD COLUMN IF NOT EXISTS timezone text DEFAULT 'America/New_York',
ADD COLUMN IF NOT EXISTS currency text DEFAULT 'USD';
"""

try:
    result = supabase.rpc("exec_sql", {"sql": sql}).execute()
    print("Migration completed successfully!")
    print(f"Result: {result.data}")
except Exception as e:
    print(f"Migration failed: {e}")
    # Try alternative method
    try:
        print("Trying alternative method...")
        # Use PostgREST to execute SQL
        result = supabase.postgrest.rpc("exec_sql", {"sql": sql}).execute()
        print("Alternative method succeeded!")
        print(f"Result: {result.data}")
    except Exception as e2:
        print(f"Alternative method also failed: {e2}")
        print("Manual migration required through Supabase dashboard")
