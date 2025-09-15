-- Remove API-related fields and add new business settings fields
ALTER TABLE public.company_profiles 
  DROP COLUMN IF EXISTS api_key,
  DROP COLUMN IF EXISTS api_secret,
  DROP COLUMN IF EXISTS platform,
  DROP COLUMN IF EXISTS additional_config;

-- Add new business settings fields
ALTER TABLE public.company_profiles 
  ADD COLUMN IF NOT EXISTS address text,
  ADD COLUMN IF NOT EXISTS website text,
  ADD COLUMN IF NOT EXISTS timezone text DEFAULT 'America/New_York',
  ADD COLUMN IF NOT EXISTS currency text DEFAULT 'USD';
