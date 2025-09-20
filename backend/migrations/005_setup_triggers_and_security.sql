-- =====================================================
-- Apply updated_at Triggers (Idempotent)
-- =====================================================

-- Sectors
DROP TRIGGER IF EXISTS update_sectors_updated_at ON sectors;
CREATE TRIGGER update_sectors_updated_at
    BEFORE UPDATE ON sectors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Agent Voices
DROP TRIGGER IF EXISTS update_agent_voices_updated_at ON agent_voices;
CREATE TRIGGER update_agent_voices_updated_at
    BEFORE UPDATE ON agent_voices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Integration Providers
DROP TRIGGER IF EXISTS update_integration_providers_updated_at ON integration_providers;
CREATE TRIGGER update_integration_providers_updated_at
    BEFORE UPDATE ON integration_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Agent Templates
DROP TRIGGER IF EXISTS update_agent_templates_updated_at ON agent_templates;
CREATE TRIGGER update_agent_templates_updated_at
    BEFORE UPDATE ON agent_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Company Agents
DROP TRIGGER IF EXISTS update_company_agents_updated_at ON company_agents;
CREATE TRIGGER update_company_agents_updated_at
    BEFORE UPDATE ON company_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Company Integrations
DROP TRIGGER IF EXISTS update_company_integrations_updated_at ON company_integrations;
CREATE TRIGGER update_company_integrations_updated_at
    BEFORE UPDATE ON company_integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Company Agent Integrations
DROP TRIGGER IF EXISTS update_company_agent_integrations_updated_at ON company_agent_integrations;
CREATE TRIGGER update_company_agent_integrations_updated_at
    BEFORE UPDATE ON company_agent_integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Agent Webhooks
DROP TRIGGER IF EXISTS update_agent_webhooks_updated_at ON agent_webhooks;
CREATE TRIGGER update_agent_webhooks_updated_at
    BEFORE UPDATE ON agent_webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Agent Training Data
DROP TRIGGER IF EXISTS update_agent_training_data_updated_at ON agent_training_data;
CREATE TRIGGER update_agent_training_data_updated_at
    BEFORE UPDATE ON agent_training_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
