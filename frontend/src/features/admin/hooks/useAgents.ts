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
    // Fallback to profile id if company id is not available
    if (profile?.id) {
      return profile.id;
    }
    // Otherwise, we might need to fetch it or use a different method
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
      setAvailableTemplates(templates);
      return templates;
    } catch (err) {
      console.error("Failed to load agent templates:", err);
      return [];
    }
  };

  const loadCompanyAgents = async () => {
    const companyId = await getCompanyId();
    console.log("loadCompanyAgents - Company ID:", companyId);
    console.log("loadCompanyAgents - Profile:", profile);
    if (!companyId) return;

    try {
      const data = await AgentService.loadCompanyAgents(companyId);
      console.log("Loaded company agents:", data);
      setCompanyAgents(data.agents || []);
      
      // Also convert and update legacy agents format for compatibility
      const legacyAgents = convertCompanyAgentsToLegacy(data.agents || []);
      console.log("Converted legacy agents:", legacyAgents);
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

  // Convert company agents to legacy format for compatibility
  const convertCompanyAgentsToLegacy = (companyAgents: any[]): AgentType[] => {
    return companyAgents.map((agent) => ({
      id: agent.id,
      name: agent.custom_name || agent.template_name || agent.name,
      description: agent.template_description || agent.description || "",
      icon: agent.icon || "default",
      color: "bg-blue-500",
      category: agent.sector_slug || "general",
      communicationType: agent.agent_type as any,
      isActive: agent.is_active || false,
      lastUpdated: new Date(agent.updated_at || agent.created_at).toISOString().split("T")[0],
      requiredIntegrations: agent.required_integrations || [],
      settings: {
        customName: agent.custom_name || agent.template_name || agent.name,
        language: "Turkish",
        enableAnalytics: true,
        integrationConfigs: agent.configuration || {},
      },
    }));
  };

  const activateAgent = async (agentTemplateId: string, config?: any) => {
    const companyId = await getCompanyId();
    if (!companyId) {
      setError("Company ID not found");
      return null;
    }

    try {
      const activatedAgent = await AgentService.activateAgent(
        companyId,
        agentTemplateId,
        config
      );
      if (activatedAgent) {
        // Reload company agents to get updated list
        await loadCompanyAgents();
      }
      return activatedAgent;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to activate agent");
      return null;
    }
  };

  const toggleAgent = async (agentId: string, isActive: boolean) => {
    const companyId = await getCompanyId();

    console.log("Company ID:", companyId);
    if (!companyId) {
      setError("Company ID not found");
      return;
    }

    try {
      console.log("Toggling agent:", agentId, "Active:", isActive);
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
        
        console.log("Agent toggled successfully:", updatedAgent);
      } else {
        throw new Error("No response from server");
      }
    } catch (err) {
      console.error("Toggle agent error:", err);
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
    return await updateAgent(updatedAgent.id, updatedAgent.settings);
  };

  useEffect(() => {
    const initializeData = async () => {
      setIsLoading(true);
      try {
        await loadSectors();
        // Load company agents first as they contain the real data
        await loadCompanyAgents();

        // Only load legacy agents if we don't have company agents
        // and businessCategory is provided
        if (businessCategory && companyAgents.length === 0) {
          await loadAgents();
        }
      } catch (err) {
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
    agents: agents.length > 0 ? agents : convertCompanyAgentsToLegacy(companyAgents),
    isLoading,
    error,
    activeAgentsCount: activeAgentsCount || legacyActiveCount,
    totalAgentsCount: totalAgentsCount || agents.length,
    toggleAgent,
    updateAgent: updateAgentLegacy,
    refetch: loadCompanyAgents, // Changed to load company agents instead

    // New methods
    updateAgentConfig: updateAgent,
    refreshCompanyAgents: loadCompanyAgents,
  };
};
