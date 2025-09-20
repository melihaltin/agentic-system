-- Migration: 004_create_advanced_tables.sql
-- Description: Create advanced tables for interactions, integrations, and logs
-- Date: 2025-09-20
-- Depends on: 002_create_agent_tables.sql, 003_update_company_profile.sql

-- =====================================================
-- 1. Agent Interactions Table
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    
    interaction_type VARCHAR(50) NOT NULL,
    session_id VARCHAR(255),
    
    -- Interaction Details
    customer_identifier VARCHAR(255),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    
    -- Content
    transcript TEXT,
    summary TEXT,
    sentiment VARCHAR(20),
    
    -- Cost
    cost DECIMAL(10,4),
    tokens_used INTEGER,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. Company Integrations Table
-- =====================================================
CREATE TABLE IF NOT EXISTS company_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    provider_id UUID NOT NULL REFERENCES integration_providers(id) ON DELETE CASCADE,
    
    -- Encrypted Credentials
    encrypted_credentials JSONB NOT NULL,
    
    -- OAuth Tokens (if applicable)
    oauth_access_token TEXT,
    oauth_refresh_token TEXT,
    oauth_token_expires_at TIMESTAMPTZ,
    
    -- Integration Status
    status VARCHAR(50) DEFAULT 'pending',
    last_verified_at TIMESTAMPTZ,
    last_sync_at TIMESTAMPTZ,
    
    -- Test and Validation
    is_test_mode BOOLEAN DEFAULT false,
    connection_tested_at TIMESTAMPTZ,
    connection_test_result JSONB,
    
    -- Metadata
    webhook_endpoint_url TEXT,
    rate_limit_remaining INTEGER,
    rate_limit_reset_at TIMESTAMPTZ,
    
    error_message TEXT,
    error_occurred_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_id, provider_id)
);

-- =====================================================
-- 3. Company Agent Integrations Table
-- =====================================================
CREATE TABLE IF NOT EXISTS company_agent_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    company_integration_id UUID NOT NULL REFERENCES company_integrations(id) ON DELETE CASCADE,
    
    is_active BOOLEAN DEFAULT true,
    
    -- Special permissions (subset of provider's features)
    allowed_operations JSONB DEFAULT '[]',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_agent_id, company_integration_id)
);

-- =====================================================
-- 4. Agent Webhooks Table
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    
    event_type VARCHAR(50) NOT NULL,
    webhook_url TEXT NOT NULL,
    headers JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT true,
    retry_count INTEGER DEFAULT 3,
    
    last_triggered_at TIMESTAMPTZ,
    last_status_code INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 5. Agent Training Data Table
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_training_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    
    data_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    
    file_url TEXT,
    file_type VARCHAR(50),
    
    is_processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 6. Integration Logs Table
-- =====================================================
CREATE TABLE IF NOT EXISTS integration_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_integration_id UUID NOT NULL REFERENCES company_integrations(id) ON DELETE CASCADE,
    company_agent_id UUID REFERENCES company_agents(id) ON DELETE SET NULL,
    
    -- Operation Details
    operation_type VARCHAR(100) NOT NULL,
    request_method VARCHAR(10),
    request_endpoint TEXT,
    request_payload JSONB,
    
    -- Result
    response_status_code INTEGER,
    response_body JSONB,
    response_time_ms INTEGER,
    
    -- Status
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 7. API Key Rotation History Table
-- =====================================================
CREATE TABLE IF NOT EXISTS api_key_rotation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_integration_id UUID NOT NULL REFERENCES company_integrations(id) ON DELETE CASCADE,
    
    action VARCHAR(50) NOT NULL,
    performed_by UUID,
    ip_address INET,
    user_agent TEXT,
    
    reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES for Advanced Tables
-- =====================================================

-- Agent Interactions indexes
CREATE INDEX IF NOT EXISTS idx_agent_interactions_company_agent_id ON agent_interactions(company_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_started_at ON agent_interactions(started_at);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_session_id ON agent_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_interaction_type ON agent_interactions(interaction_type);

-- Company Integrations indexes
CREATE INDEX IF NOT EXISTS idx_company_integrations_company_id ON company_integrations(company_id);
CREATE INDEX IF NOT EXISTS idx_company_integrations_provider_id ON company_integrations(provider_id);
CREATE INDEX IF NOT EXISTS idx_company_integrations_status ON company_integrations(status);

-- Company Agent Integrations indexes
CREATE INDEX IF NOT EXISTS idx_company_agent_integrations_agent_id ON company_agent_integrations(company_agent_id);
CREATE INDEX IF NOT EXISTS idx_company_agent_integrations_integration_id ON company_agent_integrations(company_integration_id);

-- Integration Logs indexes
CREATE INDEX IF NOT EXISTS idx_integration_logs_company_integration_id ON integration_logs(company_integration_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_created_at ON integration_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_integration_logs_status ON integration_logs(status);

-- Agent Webhooks indexes
CREATE INDEX IF NOT EXISTS idx_agent_webhooks_company_agent_id ON agent_webhooks(company_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_webhooks_event_type ON agent_webhooks(event_type);

-- Agent Training Data indexes
CREATE INDEX IF NOT EXISTS idx_agent_training_data_company_agent_id ON agent_training_data(company_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_training_data_data_type ON agent_training_data(data_type);
CREATE INDEX IF NOT EXISTS idx_agent_training_data_is_processed ON agent_training_data(is_processed);
