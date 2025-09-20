-- Migration: 003_update_company_profile.sql
-- Description: Update company_profile table to work with new agent system
-- Date: 2025-09-20
-- Depends on: 001_create_base_tables.sql

-- =====================================================
-- Update Company Profile Table
-- =====================================================

-- Add sector_id column if it doesn't exist
ALTER TABLE company_profile 
ADD COLUMN IF NOT EXISTS sector_id UUID REFERENCES sectors(id) ON DELETE SET NULL;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_company_profile_user_id ON company_profile(user_id);
CREATE INDEX IF NOT EXISTS idx_company_profile_sector_id ON company_profile(sector_id);
CREATE INDEX IF NOT EXISTS idx_company_profile_business_category ON company_profile(business_category);

-- Update existing records to link with sectors based on business_category
UPDATE company_profile 
SET sector_id = (
    SELECT id FROM sectors 
    WHERE sectors.slug = company_profile.business_category 
    OR LOWER(sectors.name) LIKE '%' || LOWER(company_profile.business_category) || '%'
    LIMIT 1
)
WHERE sector_id IS NULL AND business_category IS NOT NULL;
