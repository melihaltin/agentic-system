import { AgentType, AgentCommunicationType, VoiceAgentSettings, ChatAgentSettings } from '@/types/admin.types';
import { AGENT_COMMUNICATION_TYPES } from '../constants/agent-types';

/**
 * Check if an agent supports voice features
 */
export const isVoiceAgent = (agent: AgentType): boolean => {
  return agent.communicationType === AGENT_COMMUNICATION_TYPES.VOICE || 
         agent.communicationType === AGENT_COMMUNICATION_TYPES.HYBRID;
};

/**
 * Check if an agent supports chat features
 */
export const isChatAgent = (agent: AgentType): boolean => {
  return agent.communicationType === AGENT_COMMUNICATION_TYPES.CHAT || 
         agent.communicationType === AGENT_COMMUNICATION_TYPES.HYBRID;
};

/**
 * Check if settings are for a voice agent
 */
export const isVoiceSettings = (settings: any): settings is VoiceAgentSettings => {
  return 'voice' in settings && 'personality' in settings;
};

/**
 * Check if settings are for a chat agent  
 */
export const isChatSettings = (settings: any): settings is ChatAgentSettings => {
  return !('voice' in settings) && !('personality' in settings);
};

/**
 * Get available configuration tabs for an agent
 */
export const getAgentConfigTabs = (agent: AgentType) => {
  const baseTabs = [
    { id: 'general', label: 'General Settings', icon: '⚙️' },
    { id: 'integrations', label: 'Integrations', icon: '🔗' },
  ];

  if (isVoiceAgent(agent)) {
    baseTabs.splice(1, 0, { id: 'voice', label: 'Voice & Language', icon: '🗣️' });
  }

  return baseTabs;
};

/**
 * Get display name for agent communication type
 */
export const getAgentTypeDisplayName = (type: AgentCommunicationType): string => {
  switch (type) {
    case AGENT_COMMUNICATION_TYPES.VOICE:
      return 'Voice Agent';
    case AGENT_COMMUNICATION_TYPES.CHAT:
      return 'Chat Agent';
    case AGENT_COMMUNICATION_TYPES.HYBRID:
      return 'Voice & Chat Agent';
    default:
      return 'Unknown Agent Type';
  }
};
