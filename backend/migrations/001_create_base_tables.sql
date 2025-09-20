-- Migration: 001_create_base_tables.sql
-- Description: Create basic tables for sectors, integration providers, and agent voices
-- Date: 2025-09-20

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enable moddatetime for automatic updated_at triggers
CREATE EXTENSION IF NOT EXISTS moddatetime SCHEMA extensions;

-- =====================================================
-- 1. Sectors Table (Sektörler)
-- =====================================================
CREATE TABLE IF NOT EXISTS sectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. Agent Voices Table (Sesler)
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_voices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    voice_id VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'tr-TR',
    gender VARCHAR(20),
    age_group VARCHAR(20),
    accent VARCHAR(50),
    sample_url TEXT,
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


ALTER TABLE agent_voices
ADD CONSTRAINT uq_agent_voices_voice_provider UNIQUE (voice_id, provider);

-- =====================================================
-- 3. Integration Providers Table
-- =====================================================
CREATE TABLE IF NOT EXISTS integration_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    logo_url TEXT,
    description TEXT,
    documentation_url TEXT,
    required_credentials JSONB NOT NULL,
    oauth_enabled BOOLEAN DEFAULT false,
    oauth_authorize_url TEXT,
    oauth_token_url TEXT,
    oauth_scopes TEXT[],
    applicable_sectors UUID[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_beta BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES for Base Tables
-- =====================================================

-- Sectors indexes
CREATE INDEX IF NOT EXISTS idx_sectors_slug ON sectors(slug);
CREATE INDEX IF NOT EXISTS idx_sectors_is_active ON sectors(is_active);

-- Agent Voices indexes
CREATE INDEX IF NOT EXISTS idx_agent_voices_is_active ON agent_voices(is_active);
CREATE INDEX IF NOT EXISTS idx_agent_voices_provider ON agent_voices(provider);
CREATE INDEX IF NOT EXISTS idx_agent_voices_voice_id ON agent_voices(voice_id, provider);

-- Integration Providers indexes
CREATE INDEX IF NOT EXISTS idx_integration_providers_slug ON integration_providers(slug);
CREATE INDEX IF NOT EXISTS idx_integration_providers_category ON integration_providers(category);
CREATE INDEX IF NOT EXISTS idx_integration_providers_is_active ON integration_providers(is_active);

-- =====================================================
-- SAMPLE DATA for Base Tables
-- =====================================================

-- Insert sectors
INSERT INTO sectors (name, slug, description, icon) VALUES
('E-Commerce', 'e-commerce', 'Online retail and shopping platforms', 'shopping-cart'),
('Car Rental', 'car-rental', 'Vehicle rental and fleet management', 'car'),
('Real Estate', 'real-estate', 'Property management and real estate services', 'home'),
('Healthcare', 'healthcare', 'Medical and healthcare services', 'heart'),
('Finance', 'finance', 'Financial services and banking', 'dollar-sign')
ON CONFLICT (slug) DO NOTHING;

-- Insert voice samples
INSERT INTO agent_voices (name, provider, voice_id, language, gender, age_group) VALUES
('Ayşe - Genç Kadın', 'elevenlabs', 'voice_123', 'tr-TR', 'female', 'young'),
('Mehmet - Orta Yaş Erkek', 'elevenlabs', 'voice_456', 'tr-TR', 'male', 'middle'),
('Zeynep - Profesyonel', 'google', 'tr-TR-Standard-C', 'tr-TR', 'female', 'middle'),
('Can - Samimi', 'azure', 'tr-TR-AhmetNeural', 'tr-TR', 'male', 'young')
ON CONFLICT (voice_id, provider) DO NOTHING;

-- Insert integration providers
INSERT INTO integration_providers (name, slug, category, description, required_credentials, applicable_sectors) VALUES
(
    'Shopify', 
    'shopify', 
    'e-commerce', 
    'Shopify mağaza entegrasyonu',
    '{"api_key": {"required": true, "label": "Admin API Access Token", "type": "password", "placeholder": "shpat_xxxxx"}, 
      "store_url": {"required": true, "label": "Store URL", "type": "url", "placeholder": "mystore.myshopify.com"},
      "api_version": {"required": false, "label": "API Version", "type": "text", "default": "2024-01"}}'::jsonb,
    ARRAY((SELECT id FROM sectors WHERE slug = 'e-commerce'))
),
(
    'WooCommerce', 
    'woocommerce', 
    'e-commerce', 
    'WooCommerce WordPress entegrasyonu',
    '{"consumer_key": {"required": true, "label": "Consumer Key", "type": "password"},
      "consumer_secret": {"required": true, "label": "Consumer Secret", "type": "password"},
      "site_url": {"required": true, "label": "Site URL", "type": "url", "placeholder": "https://mystore.com"}}'::jsonb,
    ARRAY((SELECT id FROM sectors WHERE slug = 'e-commerce'))
),
(
    'Booking System', 
    'booking-system', 
    'car-rental', 
    'Car rental booking system integration',
    '{"api_endpoint": {"required": true, "label": "API Endpoint", "type": "url", "placeholder": "https://api.yourcarrental.com"},
      "api_key": {"required": true, "label": "API Key", "type": "password", "placeholder": "Enter your booking system API key"}}'::jsonb,
    ARRAY((SELECT id FROM sectors WHERE slug = 'car-rental'))
)
ON CONFLICT (slug) DO NOTHING;
