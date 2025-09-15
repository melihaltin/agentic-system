// Business Category (e.g., e-commerce, car-rental)
export interface BusinessCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  agents: AgentType[];
}

// Agent communication types
export type AgentCommunicationType = 'voice' | 'chat' | 'hybrid';

// Specific agent within a business category
export interface AgentType {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  category: string; // Business category this agent belongs to
  communicationType: AgentCommunicationType; // voice, chat, or hybrid
  isActive: boolean;
  lastUpdated: string;
  requiredIntegrations: Integration[]; // Required platform integrations
  settings: AgentSettings;
}

// Base settings for all agents
export interface BaseAgentSettings {
  customName: string; // Customer can name their agent
  language: string;
  enableAnalytics: boolean;
  customPrompt?: string;
  integrationConfigs: { [key: string]: any }; // Platform-specific configurations
}

// Voice-specific settings (only for voice and hybrid agents)
export interface VoiceAgentSettings extends BaseAgentSettings {
  voice: VoiceOption;
  personality: string;
  responseSpeed: 'fast' | 'normal' | 'slow';
  maxSessionDuration: number; // in minutes
}

// Chat-specific settings (only for chat agents)
export interface ChatAgentSettings extends BaseAgentSettings {
  // Chat agents might have specific settings in the future
  responseStyle?: 'concise' | 'detailed' | 'conversational';
}

// Union type for all agent settings
export type AgentSettings = VoiceAgentSettings | ChatAgentSettings;

export interface VoiceOption {
  id: string;
  name: string;
  language: string;
  gender: 'male' | 'female';
  preview: string; // URL to preview audio
}

// Platform integrations required by agents
export interface Integration {
  id: string;
  name: string;
  description: string;
  type: 'platform' | 'api' | 'webhook';
  required: boolean;
  fields: IntegrationField[];
}

export interface IntegrationField {
  id: string;
  name: string;
  type: 'text' | 'password' | 'select' | 'url';
  required: boolean;
  placeholder?: string;
  options?: string[]; // For select type
  validation?: string; // Regex pattern
}

export interface BusinessSettings {
  companyName: string;
  companyEmail: string;
  companyPhone: string;
  businessCategory: string;
  address?: string;
  website?: string;
  timezone: string;
  currency: string;
}

export interface AdminStats {
  totalAgents: number;
  activeAgents: number;
  totalConversations: number;
  avgResponseTime: number; // in seconds
  customerSatisfaction: number; // percentage
  monthlyCalls: number;
}

export type AdminSection = 'business-settings' | 'my-agents' | 'analytics' | 'settings';
