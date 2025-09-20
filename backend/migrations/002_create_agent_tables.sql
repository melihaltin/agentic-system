-- Migration: 002_create_agent_tables.sql
-- Description: Create agent templates and company agent tables
-- Date: 2025-09-20
-- Depends on: 001_create_base_tables.sql

-- =====================================================
-- 1. Agent Templates Table
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    
    -- Agent Capabilities
    capabilities JSONB DEFAULT '[]',
    
    -- Agent Properties
    default_prompt TEXT,
    default_voice_id UUID REFERENCES agent_voices(id) ON DELETE SET NULL,
    requires_voice BOOLEAN DEFAULT false,
    
    -- Pricing
    pricing_model VARCHAR(50),
    base_price DECIMAL(10,2),
    
    -- Metadata
    icon VARCHAR(255),
    preview_image VARCHAR(255),
    tags TEXT[],
    configuration_schema JSONB,
    
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. Company Agents Table
-- =====================================================
CREATE TABLE IF NOT EXISTS company_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    
    -- Agent Customization
    custom_name VARCHAR(100),
    custom_prompt TEXT,
    selected_voice_id UUID REFERENCES agent_voices(id) ON DELETE SET NULL,
    
    -- Configuration
    configuration JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_configured BOOLEAN DEFAULT false,
    
    -- Statistics
    total_interactions INTEGER DEFAULT 0,
    total_minutes_used DECIMAL(10,2) DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    -- Limits
    monthly_limit INTEGER,
    daily_limit INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    
    UNIQUE(company_id, agent_template_id)
);

-- =====================================================
-- 3. Sector Agent Availability Table
-- =====================================================
CREATE TABLE IF NOT EXISTS sector_agent_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    
    is_recommended BOOLEAN DEFAULT false,
    availability_status VARCHAR(50) DEFAULT 'available',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(sector_id, agent_template_id)
);

-- =====================================================
-- 4. Integration Agent Mappings Table
-- =====================================================
CREATE TABLE IF NOT EXISTS integration_agent_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES integration_providers(id) ON DELETE CASCADE,
    
    is_required BOOLEAN DEFAULT false,
    enabled_features JSONB DEFAULT '[]',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(agent_template_id, provider_id)
);

-- =====================================================
-- INDEXES for Agent Tables
-- =====================================================

-- Agent Templates indexes
CREATE INDEX IF NOT EXISTS idx_agent_templates_sector_id ON agent_templates(sector_id);
CREATE INDEX IF NOT EXISTS idx_agent_templates_agent_type ON agent_templates(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_templates_is_active ON agent_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_agent_templates_slug ON agent_templates(slug);
CREATE INDEX IF NOT EXISTS idx_agent_templates_is_featured ON agent_templates(is_featured);

-- Company Agents indexes
CREATE INDEX IF NOT EXISTS idx_company_agents_company_id ON company_agents(company_id);
CREATE INDEX IF NOT EXISTS idx_company_agents_template_id ON company_agents(agent_template_id);
CREATE INDEX IF NOT EXISTS idx_company_agents_is_active ON company_agents(is_active);
CREATE INDEX IF NOT EXISTS idx_company_agents_activated_at ON company_agents(activated_at);

-- Sector Agent Availability indexes
CREATE INDEX IF NOT EXISTS idx_sector_agent_availability_sector_id ON sector_agent_availability(sector_id);
CREATE INDEX IF NOT EXISTS idx_sector_agent_availability_template_id ON sector_agent_availability(agent_template_id);

-- Integration Agent Mappings indexes
CREATE INDEX IF NOT EXISTS idx_integration_agent_mappings_template_id ON integration_agent_mappings(agent_template_id);
CREATE INDEX IF NOT EXISTS idx_integration_agent_mappings_provider_id ON integration_agent_mappings(provider_id);

-- =====================================================
-- SAMPLE AGENT TEMPLATES
-- =====================================================

-- Insert sample agent templates
INSERT INTO agent_templates (
    name, slug, description, sector_id, agent_type, capabilities, 
    default_prompt, requires_voice, pricing_model, base_price, 
    icon, tags, configuration_schema, is_active, is_featured
) 
SELECT 
    'Voice Shopping Assistant',
    'ecommerce-voice-assistant',
    'Voice-activated shopping assistant for hands-free browsing',
    s.id,
    'voice',
    '["voice_call", "product_search", "order_tracking"]'::jsonb,
    'You are a helpful shopping assistant. Help customers find products and complete their purchases.',
    true,
    'per_minute',
    0.25,
    'shopping-cart',
    ARRAY['voice', 'shopping', 'e-commerce'],
    '{"personality": {"type": "select", "options": ["Friendly", "Professional", "Casual"], "default": "Friendly"}, "max_session_duration": {"type": "number", "min": 5, "max": 60, "default": 20}}'::jsonb,
    true,
    true
FROM sectors s WHERE s.slug = 'e-commerce'
ON CONFLICT (slug) DO NOTHING;

INSERT INTO agent_templates (
    name, slug, description, sector_id, agent_type, capabilities, 
    default_prompt, requires_voice, pricing_model, base_price, 
    icon, tags, configuration_schema, is_active, is_featured
) 
SELECT 
    'Abandoned Cart Recovery',
    'ecommerce-abandoned-cart',
    'Automated system to recover abandoned shopping carts',
    s.id,
    'voice',
    '["voice_call", "cart_recovery", "product_recommendation"]'::jsonb,
    'You are a friendly assistant helping customers complete their abandoned purchases.',
    true,
    'per_minute',
    0.30,
    'shopping-cart',
    ARRAY['voice', 'recovery', 'e-commerce'],
    '{"personality": {"type": "select", "options": ["Friendly", "Professional", "Casual"], "default": "Friendly"}, "max_session_duration": {"type": "number", "min": 5, "max": 30, "default": 15}}'::jsonb,
    true,
    false
FROM sectors s WHERE s.slug = 'e-commerce'
ON CONFLICT (slug) DO NOTHING;

INSERT INTO agent_templates (
    name, slug, description, sector_id, agent_type, capabilities, 
    default_prompt, requires_voice, pricing_model, base_price, 
    icon, tags, configuration_schema, is_active, is_featured
) 
SELECT 
    'Booking Assistant',
    'car-rental-booking',
    'Help customers find and book rental vehicles',
    s.id,
    'voice',
    '["voice_call", "vehicle_search", "booking_management"]'::jsonb,
    'You are a professional car rental assistant helping customers find and book vehicles.',
    true,
    'per_minute',
    0.35,
    'car',
    ARRAY['voice', 'booking', 'car-rental'],
    '{"personality": {"type": "select", "options": ["Professional", "Friendly"], "default": "Professional"}, "max_session_duration": {"type": "number", "min": 10, "max": 45, "default": 20}}'::jsonb,
    true,
    true
FROM sectors s WHERE s.slug = 'car-rental'
ON CONFLICT (slug) DO NOTHING;
