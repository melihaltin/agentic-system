#!/usr/bin/env python3

import os
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(url, service_key)

# Add missing columns to company_profile table
sql = """

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- EXISTING TABLE (Mevcut Tablo)
-- =====================================================

-- Company Profile Table (Zaten var olan tablo)
CREATE TABLE IF NOT EXISTS company_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50),
    business_category VARCHAR(100), -- Bu artık sector_id ile ilişkilendirilecek
    sector_id UUID REFERENCES sectors(id) ON DELETE SET NULL, -- Yeni alan eklendi
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    address TEXT,
    website TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC'
);

-- =====================================================
-- NEW TABLES (Yeni Tablolar)
-- =====================================================

-- 1. Sectors Table (Sektörler)
-- E-ticaret, Finans, Sağlık vb. sektörleri tutar
CREATE TABLE sectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE, -- URL friendly version
    description TEXT,
    icon VARCHAR(255), -- Sektör ikonu URL'si
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Agent Voices Table (Sesler)
-- Farklı ses seçeneklerini tutar
CREATE TABLE agent_voices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL, -- 'elevenlabs', 'google', 'azure' vb.
    voice_id VARCHAR(255) NOT NULL, -- Provider'daki ses ID'si
    language VARCHAR(10) DEFAULT 'tr-TR',
    gender VARCHAR(20), -- 'male', 'female', 'neutral'
    age_group VARCHAR(20), -- 'young', 'middle', 'old'
    accent VARCHAR(50), -- Aksan bilgisi
    sample_url TEXT, -- Ses örneği URL'si
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB, -- Ek özellikler için
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Agent Templates Table (Agent Şablonları)
-- Sistemde tanımlı agent tiplerini tutar
CREATE TABLE agent_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL, -- 'voice', 'chat', 'hybrid'
    
    -- Agent Yetenekleri
    capabilities JSONB DEFAULT '[]', -- ['voice_call', 'chat', 'email', 'sms']
    
    -- Agent Özellikleri
    default_prompt TEXT, -- Varsayılan sistem prompt'u
    default_voice_id UUID REFERENCES agent_voices(id) ON DELETE SET NULL,
    requires_voice BOOLEAN DEFAULT false,
    
    -- Fiyatlandırma
    pricing_model VARCHAR(50), -- 'per_minute', 'per_message', 'monthly'
    base_price DECIMAL(10,2),
    
    -- Metadata
    icon VARCHAR(255),
    preview_image VARCHAR(255),
    tags TEXT[], -- Etiketler için array
    configuration_schema JSONB, -- Agent'a özgü ayarlar şeması
    
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Company Agents Table (Şirket Agent'ları)
-- Şirketlerin aktif ettiği agent'ları tutar
CREATE TABLE company_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES company_profile(id) ON DELETE CASCADE,
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    
    -- Agent Özelleştirmeleri
    custom_name VARCHAR(100), -- Şirketin agent'a verdiği isim
    custom_prompt TEXT, -- Özelleştirilmiş prompt
    selected_voice_id UUID REFERENCES agent_voices(id) ON DELETE SET NULL,
    
    -- Konfigürasyon
    configuration JSONB DEFAULT '{}', -- Agent'a özgü ayarlar
    
    -- Durumlar
    is_active BOOLEAN DEFAULT true,
    is_configured BOOLEAN DEFAULT false, -- Tüm gerekli ayarlar yapıldı mı?
    
    -- İstatistikler
    total_interactions INTEGER DEFAULT 0,
    total_minutes_used DECIMAL(10,2) DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    -- Limitler
    monthly_limit INTEGER, -- Aylık kullanım limiti
    daily_limit INTEGER, -- Günlük kullanım limiti
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ, -- İlk aktif edilme tarihi
    
    UNIQUE(company_id, agent_template_id) -- Bir şirket aynı agent'ı iki kez ekleyemez
);

-- 5. Agent Interactions Table (Agent Etkileşimleri)
-- Tüm agent etkileşimlerini loglar
CREATE TABLE agent_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    
    interaction_type VARCHAR(50) NOT NULL, -- 'voice_call', 'chat', 'email', 'sms'
    session_id VARCHAR(255), -- Oturum ID'si
    
    -- Etkileşim Detayları
    customer_identifier VARCHAR(255), -- Müşteri telefon/email/id
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    
    -- İçerik
    transcript TEXT, -- Konuşma metni
    summary TEXT, -- AI tarafından oluşturulan özet
    sentiment VARCHAR(20), -- 'positive', 'negative', 'neutral'
    
    -- Maliyet
    cost DECIMAL(10,4),
    tokens_used INTEGER,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Sector Agent Availability Table (Sektör-Agent İlişkisi)
-- Hangi sektörde hangi agent'lar mevcut
CREATE TABLE sector_agent_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    
    is_recommended BOOLEAN DEFAULT false, -- Önerilen agent mı?
    availability_status VARCHAR(50) DEFAULT 'available', -- 'available', 'coming_soon', 'beta'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(sector_id, agent_template_id)
);

-- 7. Agent Webhooks Table (Webhook Ayarları)
-- Agent olayları için webhook tanımları
CREATE TABLE agent_webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    
    event_type VARCHAR(50) NOT NULL, -- 'call_started', 'call_ended', 'message_received'
    webhook_url TEXT NOT NULL,
    headers JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT true,
    retry_count INTEGER DEFAULT 3,
    
    last_triggered_at TIMESTAMPTZ,
    last_status_code INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Agent Training Data Table (Agent Eğitim Verileri)
-- Şirketlerin agent'larını özelleştirmek için yükledikleri veriler
CREATE TABLE agent_training_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    
    data_type VARCHAR(50) NOT NULL, -- 'faq', 'product_catalog', 'knowledge_base'
    content TEXT NOT NULL,
    
    file_url TEXT, -- Yüklenen dosya URL'si
    file_type VARCHAR(50), -- 'pdf', 'csv', 'txt'
    
    is_processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Integration Providers Table (Entegrasyon Sağlayıcıları)
-- Sistem genelinde kullanılabilir entegrasyonlar
CREATE TABLE integration_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL, -- 'Shopify', 'WooCommerce', 'Magento', 'Trendyol', 'N11'
    slug VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL, -- 'e-commerce', 'crm', 'erp', 'marketplace'
    
    -- Provider Bilgileri
    logo_url TEXT,
    description TEXT,
    documentation_url TEXT,
    
    -- Gerekli Kimlik Bilgileri Şeması
    required_credentials JSONB NOT NULL, 
    -- Örnek: {
    --   "api_key": {"required": true, "label": "API Key", "type": "password"},
    --   "api_secret": {"required": true, "label": "API Secret", "type": "password"},
    --   "store_url": {"required": true, "label": "Store URL", "type": "url"},
    --   "webhook_secret": {"required": false, "label": "Webhook Secret", "type": "password"}
    -- }
    
    -- OAuth bilgileri (varsa)
    oauth_enabled BOOLEAN DEFAULT false,
    oauth_authorize_url TEXT,
    oauth_token_url TEXT,
    oauth_scopes TEXT[],
    
    -- Hangi sektörler için uygun
    applicable_sectors UUID[] DEFAULT '{}', -- sectors tablosundaki ID'ler
    
    is_active BOOLEAN DEFAULT true,
    is_beta BOOLEAN DEFAULT false,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. Company Integrations Table (Şirket Entegrasyonları)
-- Şirketlerin kurduğu entegrasyonlar ve API anahtarları (ŞİFRELENMİŞ)
CREATE TABLE company_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES company_profile(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES integration_providers(id) ON DELETE CASCADE,
    
    -- Şifrelenmiş Kimlik Bilgileri
    encrypted_credentials JSONB NOT NULL, -- pgcrypto ile şifrelenmiş
    -- Örnek şifrelenmiş veri:
    -- {
    --   "api_key": "encrypted_value_here",
    --   "api_secret": "encrypted_value_here",
    --   "store_url": "https://mystore.myshopify.com",
    --   "webhook_secret": "encrypted_value_here"
    -- }
    
    -- OAuth Token'ları (varsa)
    oauth_access_token TEXT, -- Şifrelenmiş
    oauth_refresh_token TEXT, -- Şifrelenmiş
    oauth_token_expires_at TIMESTAMPTZ,
    
    -- Entegrasyon Durumu
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'active', 'failed', 'expired', 'disabled'
    last_verified_at TIMESTAMPTZ,
    last_sync_at TIMESTAMPTZ,
    
    -- Test ve Doğrulama
    is_test_mode BOOLEAN DEFAULT false,
    connection_tested_at TIMESTAMPTZ,
    connection_test_result JSONB,
    
    -- Metadata
    webhook_endpoint_url TEXT, -- Bizim sistemimizin webhook URL'i
    rate_limit_remaining INTEGER,
    rate_limit_reset_at TIMESTAMPTZ,
    
    error_message TEXT,
    error_occurred_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_id, provider_id) -- Bir şirket aynı provider'ı bir kez ekleyebilir
);

-- 11. Integration Agent Mappings Table (Entegrasyon-Agent İlişkileri)
-- Hangi agent hangi entegrasyonları kullanabilir
CREATE TABLE integration_agent_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES integration_providers(id) ON DELETE CASCADE,
    
    is_required BOOLEAN DEFAULT false, -- Bu agent için entegrasyon zorunlu mu?
    
    -- Agent'ın bu entegrasyonda kullanabileceği özellikler
    enabled_features JSONB DEFAULT '[]',
    -- Örnek: ["read_products", "update_inventory", "create_orders", "track_shipments"]
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(agent_template_id, provider_id)
);

-- 12. Company Agent Integrations Table (Şirket Agent Entegrasyon Bağlantıları)
-- Hangi company agent hangi entegrasyonu kullanıyor
CREATE TABLE company_agent_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_agent_id UUID NOT NULL REFERENCES company_agents(id) ON DELETE CASCADE,
    company_integration_id UUID NOT NULL REFERENCES company_integrations(id) ON DELETE CASCADE,
    
    is_active BOOLEAN DEFAULT true,
    
    -- Özel izinler (provider'ın sunduğu tüm özelliklerin alt kümesi)
    allowed_operations JSONB DEFAULT '[]',
    -- Örnek: ["read_products", "read_orders"] - sadece okuma izni
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(company_agent_id, company_integration_id)
);

-- 13. Integration Logs Table (Entegrasyon Logları)
-- API çağrıları ve sonuçları
CREATE TABLE integration_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_integration_id UUID NOT NULL REFERENCES company_integrations(id) ON DELETE CASCADE,
    company_agent_id UUID REFERENCES company_agents(id) ON DELETE SET NULL,
    
    -- İşlem Detayları
    operation_type VARCHAR(100) NOT NULL, -- 'fetch_products', 'update_inventory', vs
    request_method VARCHAR(10), -- 'GET', 'POST', 'PUT', 'DELETE'
    request_endpoint TEXT,
    request_payload JSONB,
    
    -- Sonuç
    response_status_code INTEGER,
    response_body JSONB,
    response_time_ms INTEGER,
    
    -- Durum
    status VARCHAR(50) NOT NULL, -- 'success', 'failed', 'timeout'
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 14. API Key Rotation History Table (API Anahtarı Rotasyon Geçmişi)
-- Güvenlik için API key değişim geçmişi
CREATE TABLE api_key_rotation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_integration_id UUID NOT NULL REFERENCES company_integrations(id) ON DELETE CASCADE,
    
    action VARCHAR(50) NOT NULL, -- 'created', 'rotated', 'revoked'
    performed_by UUID, -- user_id of who performed the action
    ip_address INET,
    user_agent TEXT,
    
    reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES (İndeksler)
-- =====================================================

-- Company Profile Indexes
CREATE INDEX idx_company_profile_user_id ON company_profile(user_id);
CREATE INDEX idx_company_profile_business_category ON company_profile(business_category);

-- Sectors Indexes
CREATE INDEX idx_sectors_slug ON sectors(slug);
CREATE INDEX idx_sectors_is_active ON sectors(is_active);

-- Agent Templates Indexes
CREATE INDEX idx_agent_templates_sector_id ON agent_templates(sector_id);
CREATE INDEX idx_agent_templates_agent_type ON agent_templates(agent_type);
CREATE INDEX idx_agent_templates_is_active ON agent_templates(is_active);
CREATE INDEX idx_agent_templates_slug ON agent_templates(slug);

-- Company Agents Indexes
CREATE INDEX idx_company_agents_company_id ON company_agents(company_id);
CREATE INDEX idx_company_agents_template_id ON company_agents(agent_template_id);
CREATE INDEX idx_company_agents_is_active ON company_agents(is_active);

-- Agent Interactions Indexes
CREATE INDEX idx_agent_interactions_company_agent_id ON agent_interactions(company_agent_id);
CREATE INDEX idx_agent_interactions_started_at ON agent_interactions(started_at);
CREATE INDEX idx_agent_interactions_session_id ON agent_interactions(session_id);

-- Agent Voices Indexes
CREATE INDEX idx_agent_voices_is_active ON agent_voices(is_active);
CREATE INDEX idx_agent_voices_provider ON agent_voices(provider);

-- Integration Providers Indexes
CREATE INDEX idx_integration_providers_slug ON integration_providers(slug);
CREATE INDEX idx_integration_providers_category ON integration_providers(category);
CREATE INDEX idx_integration_providers_is_active ON integration_providers(is_active);

-- Company Integrations Indexes
CREATE INDEX idx_company_integrations_company_id ON company_integrations(company_id);
CREATE INDEX idx_company_integrations_provider_id ON company_integrations(provider_id);
CREATE INDEX idx_company_integrations_status ON company_integrations(status);

-- Integration Logs Indexes
CREATE INDEX idx_integration_logs_company_integration_id ON integration_logs(company_integration_id);
CREATE INDEX idx_integration_logs_created_at ON integration_logs(created_at);
CREATE INDEX idx_integration_logs_status ON integration_logs(status);

-- =====================================================
-- SECURITY - pgcrypto Extension for API Key Encryption
-- =====================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
create extension if not exists moddatetime schema extensions;

-- Şifreli veri saklamak için helper fonksiyonlar
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(encrypt(data::bytea, key::bytea, 'aes'), 'base64');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN convert_from(
        decrypt(decode(encrypted_data, 'base64'), key::bytea, 'aes'),
        'UTF8'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to all tables with updated_at column
CREATE TRIGGER update_company_profile_updated_at BEFORE UPDATE ON company_profile
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sectors_updated_at BEFORE UPDATE ON sectors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_voices_updated_at BEFORE UPDATE ON agent_voices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_templates_updated_at BEFORE UPDATE ON agent_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_agents_updated_at BEFORE UPDATE ON company_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_webhooks_updated_at BEFORE UPDATE ON agent_webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_training_data_updated_at BEFORE UPDATE ON agent_training_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) - Supabase için
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE company_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE sectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_voices ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sector_agent_availability ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_training_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_agent_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_agent_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_key_rotation_history ENABLE ROW LEVEL SECURITY;

-- Company Profile Policies
CREATE POLICY "Companies can view own profile" ON company_profile
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Companies can update own profile" ON company_profile
    FOR UPDATE USING (auth.uid() = user_id);

-- Sectors Policies (Herkes okuyabilir)
CREATE POLICY "Anyone can view active sectors" ON sectors
    FOR SELECT USING (is_active = true);

-- Agent Voices Policies (Herkes okuyabilir)
CREATE POLICY "Anyone can view active voices" ON agent_voices
    FOR SELECT USING (is_active = true);

-- Agent Templates Policies (Herkes okuyabilir)
CREATE POLICY "Anyone can view active templates" ON agent_templates
    FOR SELECT USING (is_active = true);

-- Company Agents Policies
CREATE POLICY "Companies can manage own agents" ON company_agents
    FOR ALL USING (
        company_id IN (
            SELECT id FROM company_profile WHERE user_id = auth.uid()
        )
    );

-- Agent Interactions Policies
CREATE POLICY "Companies can view own interactions" ON agent_interactions
    FOR SELECT USING (
        company_agent_id IN (
            SELECT id FROM company_agents WHERE company_id IN (
                SELECT id FROM company_profile WHERE user_id = auth.uid()
            )
        )
    );

-- Integration Providers Policies (Herkes okuyabilir)
CREATE POLICY "Anyone can view active providers" ON integration_providers
    FOR SELECT USING (is_active = true);

-- Company Integrations Policies
CREATE POLICY "Companies can manage own integrations" ON company_integrations
    FOR ALL USING (
        company_id IN (
            SELECT id FROM company_profile WHERE user_id = auth.uid()
        )
    );

-- Integration Logs Policies
CREATE POLICY "Companies can view own integration logs" ON integration_logs
    FOR SELECT USING (
        company_integration_id IN (
            SELECT id FROM company_integrations WHERE company_id IN (
                SELECT id FROM company_profile WHERE user_id = auth.uid()
            )
        )
    );

-- =====================================================
-- SAMPLE DATA (Örnek Veri)
-- =====================================================

-- Örnek Sektörler
INSERT INTO sectors (name, slug, description) VALUES
('E-Commerce', 'e-commerce', 'Online retail and shopping platforms'),
('Car Rental', 'car-rental', 'Vehicle rental and fleet management'),
('Real Estate', 'real-estate', 'Property management and real estate services'),
('Healthcare', 'healthcare', 'Medical and healthcare services'),
('Finance', 'finance', 'Financial services and banking');

-- Örnek Sesler
INSERT INTO agent_voices (name, provider, voice_id, language, gender, age_group) VALUES
('Ayşe - Genç Kadın', 'elevenlabs', 'voice_123', 'tr-TR', 'female', 'young'),
('Mehmet - Orta Yaş Erkek', 'elevenlabs', 'voice_456', 'tr-TR', 'male', 'middle'),
('Zeynep - Profesyonel', 'google', 'tr-TR-Standard-C', 'tr-TR', 'female', 'middle'),
('Can - Samimi', 'azure', 'tr-TR-AhmetNeural', 'tr-TR', 'male', 'young');

-- Örnek Entegrasyon Sağlayıcıları (Sadece Shopify)
INSERT INTO integration_providers (name, slug, category, description, required_credentials, applicable_sectors) VALUES
('Shopify', 'shopify', 'e-commerce', 'Shopify mağaza entegrasyonu', 
 '{"api_key": {"required": true, "label": "Admin API Access Token", "type": "password", "placeholder": "shpat_xxxxx"}, 
   "store_url": {"required": true, "label": "Store URL", "type": "url", "placeholder": "mystore.myshopify.com"},
   "api_version": {"required": false, "label": "API Version", "type": "text", "default": "2024-01"}}'::jsonb,
 ARRAY((SELECT id FROM sectors WHERE slug = 'e-commerce')));

-- Örnek Agent Templates
INSERT INTO agent_templates (name, slug, description, sector_id, agent_type, capabilities, default_prompt, requires_voice, pricing_model, base_price, icon, tags, configuration_schema, is_active, is_featured) 
SELECT 
  'Voice Shopping Assistant',
  'ecommerce-voice-assistant',
  'Voice-activated shopping assistant for hands-free browsing',
  (SELECT id FROM sectors WHERE slug = 'e-commerce'),
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
UNION ALL
SELECT 
  'Abandoned Cart Recovery',
  'ecommerce-abandoned-cart',
  'Automated system to recover abandoned shopping carts',
  (SELECT id FROM sectors WHERE slug = 'e-commerce'),
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
UNION ALL
SELECT 
  'Booking Assistant',
  'car-rental-booking',
  'Help customers find and book rental vehicles',
  (SELECT id FROM sectors WHERE slug = 'car-rental'),
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
  true;


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
