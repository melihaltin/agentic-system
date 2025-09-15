import { AgentType, VoiceOption, AgentSettings, BaseAgentSettings, VoiceAgentSettings, ChatAgentSettings } from '@/types/admin.types';
import { AdminApiService } from '@/lib/admin-api';

export class AgentService {
  /**
   * Load agents for a specific business category
   */
  static async loadAgents(category: string): Promise<AgentType[]> {
    try {
      return await AdminApiService.getAgentsForCategory(category);
    } catch (error) {
      console.error('Error loading agents:', error);
      throw new Error('Failed to load agents');
    }
  }

  /**
   * Toggle agent active status
   */
  static async toggleAgentStatus(agentId: string, isActive: boolean): Promise<AgentType | null> {
    try {
      const result = await AdminApiService.toggleAgentStatus(agentId, isActive);
      return result.success && result.agent ? result.agent : null;
    } catch (error) {
      console.error('Error toggling agent status:', error);
      throw new Error('Failed to update agent status');
    }
  }

  /**
   * Update agent settings
   */
  static async updateAgentSettings(agentId: string, settings: AgentSettings): Promise<AgentType | null> {
    try {
      const result = await AdminApiService.updateAgentSettings(agentId, settings);
      return result.success && result.agent ? result.agent : null;
    } catch (error) {
      console.error('Error updating agent settings:', error);
      throw new Error('Failed to update agent settings');
    }
  }

  /**
   * Load voice options for voice-enabled agents
   */
  static async loadVoiceOptions(): Promise<VoiceOption[]> {
    try {
      return await AdminApiService.getVoiceOptions();
    } catch (error) {
      console.error('Error loading voice options:', error);
      throw new Error('Failed to load voice options');
    }
  }

  /**
   * Create default settings for an agent based on its type
   */
  static createDefaultSettings(agent: AgentType): AgentSettings {
    const baseSettings: BaseAgentSettings = {
      customName: agent.name,
      language: 'English (US)',
      enableAnalytics: true,
      integrationConfigs: {},
    };

    if (agent.communicationType === 'chat') {
      const chatSettings: ChatAgentSettings = {
        ...baseSettings,
        responseStyle: 'conversational',
      };
      return chatSettings;
    } else {
      // For voice and hybrid agents
      const voiceSettings: VoiceAgentSettings = {
        ...baseSettings,
        voice: {
          id: 'default-voice',
          name: 'Default Voice',
          language: 'English (US)',
          gender: 'female',
          preview: '',
        },
        personality: 'Helpful and professional',
        responseSpeed: 'normal',
        maxSessionDuration: 30,
      };
      return voiceSettings;
    }
  }

  /**
   * Validate agent settings
   */
  static validateAgentSettings(agent: AgentType, settings: AgentSettings): string[] {
    const errors: string[] = [];

    if (!settings.customName?.trim()) {
      errors.push('Agent name is required');
    }

    if (!settings.language?.trim()) {
      errors.push('Language selection is required');
    }

    // Validate voice settings for voice-enabled agents
    if (agent.communicationType !== 'chat' && 'voice' in settings) {
      const voiceSettings = settings as VoiceAgentSettings;
      if (!voiceSettings.voice?.id) {
        errors.push('Voice selection is required for voice agents');
      }
      if (!voiceSettings.personality?.trim()) {
        errors.push('Personality is required for voice agents');
      }
    }

    // Validate required integrations
    for (const integration of agent.requiredIntegrations) {
      if (integration.required && !settings.integrationConfigs[integration.id]) {
        errors.push(`${integration.name} integration is required`);
      }
    }

    return errors;
  }
}
