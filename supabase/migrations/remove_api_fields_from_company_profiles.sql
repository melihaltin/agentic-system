-- Remove API-related fields from company_profiles table
ALTER TABLE public.company_profiles 
  DROP COLUMN IF EXISTS api_key,
  DROP COLUMN IF EXISTS api_secret,
  DROP COLUMN IF EXISTS platform,
  DROP COLUMN IF EXISTS additional_config;
