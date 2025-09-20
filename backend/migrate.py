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


CREATE TABLE IF NOT EXISTS agent_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,      -- cart_recovery, order_faq, vb.
    description TEXT,
    requires_platform BOOLEAN DEFAULT FALSE, -- platform gerekli mi
    requires_api_keys BOOLEAN DEFAULT FALSE, -- API key gerekli mi
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS platforms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,   -- Shopify, WooCommerce …
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES company_profiles(id) ON DELETE CASCADE,
    agent_type_id UUID NOT NULL REFERENCES agent_types(id),
    platform_id   UUID REFERENCES platforms(id),  -- gerekiyorsa
    display_name  VARCHAR(150),                   -- özel isimlendirme (opsiyonel)
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (company_id, agent_type_id, platform_id)
);


CREATE TABLE IF NOT EXISTS agent_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    key_name  VARCHAR(100) NOT NULL,   -- örn. shopify_api_key
    key_value TEXT NOT NULL,           -- gerçek anahtar (şifreli saklamayı unutma)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (agent_id, key_name)
);


-- Abandoned Cart Recovery agent type





CREATE TABLE IF NOT EXISTS voices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,            -- örn. "English Female", "Turkish Male"
    language_code VARCHAR(10),             -- örn. "en-US", "tr-TR" (opsiyonel)
    mp3_url TEXT NOT NULL,                  -- ses dosyasının saklandığı URL
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (name, language_code)
);



CREATE TABLE IF NOT EXISTS agent_voices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    voice_id UUID NOT NULL REFERENCES voices(id) ON DELETE CASCADE,
    is_default BOOLEAN DEFAULT FALSE,  -- agent için varsayılan ses seçeneği
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (agent_id, voice_id)
);


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
