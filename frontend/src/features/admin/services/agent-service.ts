import {
  AgentType,
  VoiceOption,
  AgentSettings,
  BaseAgentSettings,
  VoiceAgentSettings,
  ChatAgentSettings,
} from "@/types/admin.types";
import { agentsApi } from "@/lib/api/agents";

export class AgentService {
  /**
   * Load sectors
   */
  static async loadSectors(): Promise<any[]> {
    try {
      const response = await agentsApi.getSectors();
      return response.sectors || [];
    } catch (error) {
      console.error("Error loading sectors:", error);
      throw new Error("Failed to load sectors");
    }
  }

  /**
   * Load agent templates for a specific sector
   */
  static async loadAgentTemplates(sectorId: string): Promise<any[]> {
    try {
      const response = await agentsApi.getAgentTemplatesBySector(sectorId);
      return response.templates || [];
    } catch (error) {
      console.error("Error loading agent templates:", error);
      throw new Error("Failed to load agent templates");
    }
  }

  /**
   * Load company agents
   */
  static async loadCompanyAgents(companyId: string): Promise<{
    agents: any[];
    total: number;
    active_count: number;
  }> {
    try {
      return await agentsApi.getCompanyAgents(companyId);
    } catch (error) {
      console.error("Error loading company agents:", error);
      throw new Error("Failed to load company agents");
    }
  }

  /**
   * Activate agent for company
   */
  static async activateAgent(
    companyId: string,
    agentTemplateId: string,
    config?: any
  ): Promise<any> {
    try {
      const result = await agentsApi.activateAgent(
        companyId,
        agentTemplateId,
        config
      );
      return result.success ? result.agent : null;
    } catch (error) {
      console.error("Error activating agent:", error);
      throw new Error("Failed to activate agent");
    }
  }

  /**
   * Toggle agent active status
   */
  static async toggleAgentStatus(
    companyId: string,
    agentId: string,
    isActive: boolean
  ): Promise<any> {
    try {
      const result = await agentsApi.toggleAgentStatus(
        companyId,
        agentId,
        isActive
      );
      return result.success ? result.agent : null;
    } catch (error) {
      console.error("Error toggling agent status:", error);
      throw new Error("Failed to update agent status");
    }
  }

  /**
   * Update agent settings
   */
  static async updateAgentSettings(
    companyId: string,
    agentId: string,
    settings: any
  ): Promise<any> {
    try {
      const result = await agentsApi.updateCompanyAgent(
        companyId,
        agentId,
        settings
      );
      return result.success ? result.agent : null;
    } catch (error) {
      console.error("Error updating agent settings:", error);
      throw new Error("Failed to update agent settings");
    }
  }

  /**
   * Load voice options for voice-enabled agents
   */
  static async loadVoiceOptions(): Promise<VoiceOption[]> {
    try {
      const response = await agentsApi.getVoiceOptions();
      return response.voices || [];
    } catch (error) {
      console.error("Error loading voice options:", error);
      throw new Error("Failed to load voice options");
    }
  }

  /**
   * Load integration providers
   */
  static async loadIntegrationProviders(category?: string): Promise<any[]> {
    try {
      const response = await agentsApi.getIntegrationProviders(category);
      return response.providers || [];
    } catch (error) {
      console.error("Error loading integration providers:", error);
      throw new Error("Failed to load integration providers");
    }
  }

  // Legacy methods for backward compatibility with existing frontend code
  static async loadAgents(category: string): Promise<AgentType[]> {
    try {
      // This is for backward compatibility with existing code that uses categories
      // We'll need to map this to the new sector-based system
      const sectors = await this.loadSectors();
      const sector = sectors.find(
        (s) =>
          s.slug === category ||
          s.name.toLowerCase().includes(category.toLowerCase())
      );

      if (sector) {
        const templates = await this.loadAgentTemplates(sector.id);
        // Convert templates to AgentType format for compatibility
        return templates.map((template) => ({
          id: template.id,
          name: template.name,
          description: template.description,
          icon: template.icon || "default",
          color: "bg-blue-500",
          category: sector.slug,
          communicationType: template.agent_type as any,
          isActive: false, // Templates are not active by default
          lastUpdated: new Date().toISOString().split("T")[0],
          requiredIntegrations: template.required_integrations || [],
          settings: {
            customName: template.name,
            language: "Turkish",
            enableAnalytics: true,
            integrationConfigs: {},
          },
        }));
      }
      return [];
    } catch (error) {
      console.error("Error loading agents (legacy):", error);
      throw new Error("Failed to load agents");
    }
  }

  /**
   * Create default settings for an agent based on its type
   */
  static createDefaultSettings(agent: AgentType): AgentSettings {
    const baseSettings: BaseAgentSettings = {
      customName: agent.name,
      language: "Turkish",
      enableAnalytics: true,
      integrationConfigs: {},
    };

    if (agent.communicationType === "chat") {
      const chatSettings: ChatAgentSettings = {
        ...baseSettings,
        responseStyle: "conversational",
      };
      return chatSettings;
    } else {
      // For voice and hybrid agents
      const voiceSettings: VoiceAgentSettings = {
        ...baseSettings,
        voice: {
          id: "default-voice",
          name: "Default Voice",
          provider: "elevenlabs",
          voice_id: "default",
          language: "tr-TR",
          gender: "female",
          is_premium: false,
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        personality: "Helpful and professional",
        responseSpeed: "normal",
        maxSessionDuration: 30,
      };
      return voiceSettings;
    }
  }

  /**
   * Validate agent settings
   */
  static validateAgentSettings(
    agent: AgentType,
    settings: AgentSettings
  ): string[] {
    const errors: string[] = [];

    if (!settings.customName?.trim()) {
      errors.push("Agent name is required");
    }

    if (!settings.language?.trim()) {
      errors.push("Language selection is required");
    }

    // Validate voice settings for voice-enabled agents
    if (agent.communicationType !== "chat" && "voice" in settings) {
      const voiceSettings = settings as VoiceAgentSettings;
      if (!voiceSettings.voice?.id) {
        errors.push("Voice selection is required for voice agents");
      }
      if (!voiceSettings.personality?.trim()) {
        errors.push("Personality is required for voice agents");
      }
    }

    // Validate required integrations
    for (const integration of agent.requiredIntegrations) {
      if (
        integration.required &&
        !settings.integrationConfigs[integration.id]
      ) {
        errors.push(`${integration.name} integration is required`);
      }
    }

    return errors;
  }
}
