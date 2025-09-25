import { useState, useEffect } from "react";
import { AgentType } from "@/types/admin.types";
import { AgentService } from "../services/agent-service";
import { useAuthStore } from "@/store/auth";

export const useAgents = (businessCategory?: string) => {
  const [agents, setAgents] = useState<AgentType[]>([]);
  const [companyAgents, setCompanyAgents] = useState<any[]>([]);
  const [availableTemplates, setAvailableTemplates] = useState<any[]>([]);
  const [sectors, setSectors] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { profile } = useAuthStore();

  // Get company ID from profile
  const getCompanyId = async () => {
    // If we have profile with company info, use it
    if (profile?.company?.id) {
      return profile.company.id;
    }

    // If profile.company.id is not available but we have user ID,
    // we need to fetch the company profile from backend
    if (profile?.id) {
      try {
        // This should be handled by the backend, but for now use a direct approach
        // In a real app, we'd have an API endpoint to get company by user ID
        console.warn(
          "Using user ID as fallback, should fetch company ID from backend"
        );
        return profile.id;
      } catch (err) {
        console.error("Failed to get company ID:", err);
        return null;
      }
    }

    return null;
  };

  const loadSectors = async () => {
    try {
      const sectorData = await AgentService.loadSectors();
      setSectors(sectorData);
      return sectorData;
    } catch (err) {
      console.error("Failed to load sectors:", err);
      return [];
    }
  };

  const loadAgentTemplates = async (sectorId: string) => {
    try {
      const templates = await AgentService.loadAgentTemplates(sectorId);

      console.log("Loaded templates for sector", sectorId, templates);

      setAvailableTemplates(templates);
      return templates;
    } catch (err) {
      console.error("Failed to load agent templates:", err);
      return [];
    }
  };

  const loadCompanyAgents = async (templates?: any[]) => {
    const companyId = await getCompanyId();
    console.log("loadCompanyAgents - Company ID:", companyId);
    console.log("loadCompanyAgents - Profile:", profile);
    if (!companyId) return;

    try {
      const data = await AgentService.loadCompanyAgents(companyId);
      console.log("Loaded company agents:", data);
      setCompanyAgents(data.agents || []);

      // Also convert and update legacy agents format for compatibility
      // Use provided templates or current availableTemplates
      const templatesToUse = templates || availableTemplates;
      const legacyAgents = convertCompanyAgentsToLegacy(
        data.agents || [],
        templatesToUse
      );
      console.log("Converted legacy agents:", legacyAgents);
      console.log("Templates used for conversion:", templatesToUse);
      setAgents(legacyAgents);

      return data;
    } catch (err) {
      console.error("Failed to load company agents:", err);
      return null;
    }
  };

  // Legacy method for backward compatibility
  const loadAgents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (businessCategory) {
        const agentData = await AgentService.loadAgents(businessCategory);
        setAgents(agentData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load agents");
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced convert function that merges template data with company agents
  const convertCompanyAgentsToLegacy = (
    companyAgents: any[],
    templates: any[] = availableTemplates
  ): AgentType[] => {
    const normalizeLanguage = (lang: string | undefined): string => {
      if (!lang) return "tr-TR";
      const lower = lang.toLowerCase();
      // Map common names to ISO codes
      if (lower === "turkish" || lower === "türkçe" || lower === "tr")
        return "tr-TR";
      if (lower === "english" || lower === "en" || lower === "ingilizce")
        return "en-US";
      if (lower === "spanish" || lower === "es" || lower === "español")
        return "es-ES";
      if (lower === "german" || lower === "de" || lower === "deutsch")
        return "de-DE";
      if (lower === "french" || lower === "fr" || lower === "français")
        return "fr-FR";
      // If already looks like an ISO code (xx-XX), return as is
      if (/^[a-z]{2}-[A-Z]{2}$/.test(lang)) return lang;
      return "en-US";
    };

    return companyAgents.map((agent) => {
      // Template bilgilerini bul
      const templateData = templates.find(
        (template) => template.id === agent.agent_template_id
      );

      // Voice agent için ses ayarlarını hazırla
      const isVoiceAgent =
        agent.agent_type === "voice" ||
        agent.agent_type === "hybrid" ||
        templateData?.agent_type === "voice" ||
        templateData?.agent_type === "hybrid";

      console.log("isVoiceAgent:", agent);
      let voiceSettings = {};

      if (isVoiceAgent) {
        voiceSettings = {
          voice: agent.selected_voice_id
            ? {
                id: agent.selected_voice_id,
                name: agent.voice_name || "Selected Voice",
                provider:
                  agent.voice_provider ||
                  templateData?.default_voice_provider ||
                  "elevenlabs",
              }
            : templateData?.default_voice_id
            ? {
                id: templateData.default_voice_id,
                name: templateData.default_voice_name || "Default Voice",
                provider: templateData.default_voice_provider || "elevenlabs",
              }
            : null,
          personality:
            agent.personality ||
            templateData?.default_personality ||
            "Friendly",
          responseSpeed:
            agent.response_speed ||
            templateData?.default_response_speed ||
            "normal",
          maxSessionDuration:
            agent.max_session_duration ||
            templateData?.default_max_session_duration ||
            20,
        };
      }

      // Set category from sector_slug (backend provides this)

      // Set category from sector_slug (backend provides this)
      const categoryFromSlug = agent.slug || templateData?.slug || "general";
      const category = categoryFromSlug.includes("-")
        ? categoryFromSlug.split("-")[0]
        : categoryFromSlug;

      return {
        id: agent.id,
        name:
          agent.custom_name ||
          agent.template_name ||
          templateData?.name ||
          agent.name,

        originalName: templateData?.name || agent.name,

        description:
          agent.template_description ||
          templateData?.description ||
          agent.description ||
          "",
        icon: agent.icon || templateData?.icon || "default",
        color: templateData?.color || "bg-blue-500",
        category: category,
        communicationType: (agent.agent_type ||
          templateData?.agent_type) as any,
        isActive: agent.is_active || false,
        lastUpdated: new Date(agent.updated_at || agent.created_at)
          .toISOString()
          .split("T")[0],
        requiredIntegrations:
          agent.required_integrations ||
          templateData?.required_integrations ||
          [],
        agentTemplateId: agent.agent_template_id,
        isCompanyAgent: true,
        settings: {
          customName:
            agent.custom_name ||
            agent.template_name ||
            templateData?.name ||
            agent.name,
          customPrompt:
            agent.custom_prompt ||
            agent.template_prompt ||
            templateData?.default_prompt,
          language: normalizeLanguage(
            agent.language || templateData?.default_language || "tr-TR"
          ),
          enableAnalytics: agent.enable_analytics !== false,
          integrationConfigs: {
            ...templateData?.default_integrations,
            ...agent.configuration,
          },
          ...voiceSettings,
        },
        // Template'den gelen ek bilgileri de ekle
        templateInfo: templateData
          ? {
              templateId: templateData.id,
              templateName: templateData.name,
              templateDescription: templateData.description,
              templateIcon: templateData.icon,
              templateAgentType: templateData.agent_type,
              templateRequiredIntegrations: templateData.required_integrations,
              ...(agent.template_info && {
                originalTemplateInfo: agent.template_info,
              }),
            }
          : agent.template_info || undefined,
      };
    });
  };

  const activateAgent = async (agentTemplateId: string, config: any = {}) => {
    const companyId = await getCompanyId();
    if (!companyId) {
      setError("Company ID not found");
      return null;
    }

    try {
      const template = availableTemplates.find((t) => t.id === agentTemplateId);

      // Prepare configuration with integration data
      const activationConfig = {
        custom_name: config?.custom_name || template?.name,
        custom_prompt: config?.custom_prompt || template?.default_prompt,
        selected_voice_id: config?.selected_voice_id,
        language: config?.language,
        configuration: config?.configuration || {},
        integrations: config?.integrationConfigs || {},
      };

      const activatedAgent = await AgentService.activateAgent(
        companyId,
        agentTemplateId,
        activationConfig
      );

      if (activatedAgent) {
        await loadCompanyAgents();
      }
      return activatedAgent;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to activate agent");
      return null;
    }
  };

  const toggleAgent = async (
    agentId: string,
    isActive: boolean,
    agentTemplateId?: string
  ) => {
    const companyId = await getCompanyId();

    if (!companyId) {
      setError("Company ID not found");
      return;
    }

    try {
      // If this is a template (agentTemplateId provided) and we want to activate it
      if (agentTemplateId && isActive) {
        const activatedAgent = await AgentService.activateAgent(
          companyId,
          agentTemplateId,
          {
            custom_name: agents.find((a) => a.id === agentId)?.name,
            configuration: {},
          }
        );

        if (activatedAgent) {
          // Reload all agents to get the updated list
          await loadCompanyAgents();
          return;
        } else {
          throw new Error("Failed to activate template");
        }
      }

      // Regular toggle for existing company agents
      const updatedAgent = await AgentService.toggleAgentStatus(
        companyId,
        agentId,
        isActive
      );

      if (updatedAgent) {
        // Update company agents list
        setCompanyAgents((prev) =>
          prev.map((agent) =>
            agent.id === agentId ? { ...agent, is_active: isActive } : agent
          )
        );

        // Also update legacy agents list
        setAgents((prev) =>
          prev.map((agent) =>
            agent.id === agentId ? { ...agent, isActive } : agent
          )
        );
      } else {
        throw new Error("No response from server");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update agent");
      // Reload data to ensure consistency
      await loadCompanyAgents();
    }
  };

  const updateAgent = async (agentId: string, updates: any) => {
    const companyId = await getCompanyId();
    if (!companyId) {
      setError("Company ID not found");
      return null;
    }

    try {
      const result = await AgentService.updateAgentSettings(
        companyId,
        agentId,
        updates
      );
      if (result) {
        // Update company agents list
        setCompanyAgents((prev) =>
          prev.map((agent) =>
            agent.id === agentId ? { ...agent, ...updates } : agent
          )
        );
      }
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update agent");
      return null;
    }
  };

  // Legacy updateAgent for backward compatibility
  const updateAgentLegacy = async (updatedAgent: AgentType) => {
    // Company agent için doğru format hazırla
    const updates: any = {
      custom_name: updatedAgent.settings.customName,
      custom_prompt: (updatedAgent.settings as any).customPrompt,
      configuration: updatedAgent.settings.integrationConfigs,
      language: updatedAgent.settings.language,
      enable_analytics: updatedAgent.settings.enableAnalytics,
    };

    // Voice agent ise ses ayarlarını da ekle
    if (
      "voice" in updatedAgent.settings &&
      (updatedAgent.settings as any).voice
    ) {
      const voiceSettings = updatedAgent.settings as any;
      updates.selected_voice_id = voiceSettings.voice?.id;
      updates.voice_name = voiceSettings.voice?.name;
      updates.voice_provider = voiceSettings.voice?.provider;
      updates.personality = voiceSettings.personality;
      updates.response_speed = voiceSettings.responseSpeed;
      updates.max_session_duration = voiceSettings.maxSessionDuration;
    }

    const result = await updateAgent(updatedAgent.id, updates);

    // Güncelleme başarılı olduktan sonra agents listesini de güncelle
    if (result) {
      setAgents((prev) =>
        prev.map((agent) =>
          agent.id === updatedAgent.id ? updatedAgent : agent
        )
      );

      // Company agents listesini de güncelle
      setCompanyAgents((prev) =>
        prev.map((agent) =>
          agent.id === updatedAgent.id ? { ...agent, ...updates } : agent
        )
      );

      // Değişiklikten sonra company agents'ı yeniden yükle
      await loadCompanyAgents();
    }

    return result;
  };

  useEffect(() => {
    const initializeData = async () => {
      setIsLoading(true);
      try {
        const sectorsData = await loadSectors();

        // Template'leri önce yükleyelim ki convertCompanyAgentsToLegacy fonksiyonunda kullanabilelim
        let loadedTemplates: any[] = [];
        if (profile?.company?.business_category) {
          const sector = sectorsData.find(
            (s) =>
              s.slug === profile.company?.business_category ||
              s.name.toLowerCase() ===
                profile.company?.business_category?.toLowerCase()
          );

          if (sector) {
            loadedTemplates = await loadAgentTemplates(sector.id);
            console.log("Loaded templates:", loadedTemplates);
          }
        }

        // Load company agents after templates are loaded, pass templates explicitly
        const companyData = await loadCompanyAgents(loadedTemplates);

        // Template'leri legacy format'a çevir (sadece aktif olmayan template'ler için)
        if (profile?.company?.business_category && loadedTemplates.length > 0) {
          const sector = sectorsData.find(
            (s) =>
              s.slug === profile.company?.business_category ||
              s.name.toLowerCase() ===
                profile.company?.business_category?.toLowerCase()
          );

          if (sector) {
            // Company agents'ların template ID'lerini al
            const activeTemplateIds =
              companyData?.agents?.map((agent) => agent.agent_template_id) ||
              [];

            // Sadece aktif olmayan template'leri al
            const inactiveTemplates = loadedTemplates.filter(
              (template) => !activeTemplateIds.includes(template.id)
            );

            const legacyTemplates = inactiveTemplates.map((template) => {
              const isTemplateVoiceAgent =
                template.agent_type === "voice" ||
                template.agent_type === "hybrid";
              let templateVoiceSettings = {};

              if (isTemplateVoiceAgent) {
                templateVoiceSettings = {
                  voice: template.default_voice_id
                    ? {
                        id: template.default_voice_id,
                        name: template.default_voice_name || "Default Voice",
                        provider:
                          template.default_voice_provider || "elevenlabs",
                      }
                    : null,
                  personality: template.default_personality || "Friendly",
                  responseSpeed: template.default_response_speed || "normal",
                  maxSessionDuration:
                    template.default_max_session_duration || 20,
                };
              }

              return {
                id: template.id,
                name: template.name,
                description: template.description,
                icon: template.icon || "default",
                color: template.color || "bg-blue-500",
                category: sector.slug,
                communicationType: template.agent_type as any,
                isActive: false,
                lastUpdated: new Date().toISOString().split("T")[0],
                requiredIntegrations: template.required_integrations || [],
                agentTemplateId: template.id,
                isCompanyAgent: false,
                settings: {
                  customName: template.name,
                  customPrompt: template.default_prompt,
                  language: template.default_language || "Turkish",
                  enableAnalytics: true,
                  integrationConfigs: template.default_integrations || {},
                  ...templateVoiceSettings,
                },
              };
            });

            // Company agent'ları ve template'leri birleştir
            const existingAgents = convertCompanyAgentsToLegacy(
              companyData?.agents || [],
              loadedTemplates
            );
            const allAgents = [...existingAgents, ...legacyTemplates];
            console.log("Final agents with templates:", allAgents);
            setAgents(allAgents);
          }
        }

        // Only load legacy agents if we don't have company agents
        // and businessCategory is provided
        if (
          businessCategory &&
          (!companyData || companyData.agents?.length === 0)
        ) {
          await loadAgents();
        }
      } catch (err) {
        console.error("Failed to initialize agent data:", err);
        setError("Failed to initialize agent data");
      } finally {
        setIsLoading(false);
      }
    };

    initializeData();
  }, [businessCategory, profile?.company?.id, profile?.id]);

  // Computed values
  const activeAgentsCount = companyAgents.filter(
    (agent) => agent.is_active
  ).length;
  const totalAgentsCount = companyAgents.length;
  const legacyActiveCount = agents.filter((agent) => agent.isActive).length;

  return {
    // New API data
    sectors,
    availableTemplates,
    companyAgents,
    loadAgentTemplates,
    activateAgent,

    // Legacy compatibility - prioritize company agents data
    agents:
      agents.length > 0 ? agents : convertCompanyAgentsToLegacy(companyAgents),
    isLoading,
    error,
    activeAgentsCount: activeAgentsCount || legacyActiveCount,
    totalAgentsCount: totalAgentsCount || agents.length,
    toggleAgent,
    updateAgent: updateAgentLegacy,
    refetch: loadCompanyAgents,

    // New methods
    updateAgentConfig: updateAgent,
    refreshCompanyAgents: loadCompanyAgents,
  };
};
