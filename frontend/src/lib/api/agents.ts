import {
  AgentType,
  BusinessCategory,
  VoiceOption,
  AdminStats,
} from "@/types/admin.types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  // Get token from your auth system (e.g., Supabase)
  const token =
    localStorage.getItem("supabase.auth.token") ||
    sessionStorage.getItem("supabase.auth.token");

  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await response.text());
  }

  return response.json();
}

// Real API endpoints
export const agentsApi = {
  // Sectors
  getSectors: (): Promise<{ sectors: any[]; total: number }> =>
    fetchWithAuth("/v1/agents/sectors"),

  // Agent Templates
  getAgentTemplatesBySector: (
    sectorId: string
  ): Promise<{ templates: any[]; total: number }> =>
    fetchWithAuth(`/v1/agents/sectors/${sectorId}/templates`),

  // Company Agents
  getCompanyAgents: (
    companyId: string
  ): Promise<{
    agents: any[];
    total: number;
    active_count: number;
  }> => fetchWithAuth(`/v1/agents/company/${companyId}`),

  // Activate agent for company
  activateAgent: (
    companyId: string,
    agentTemplateId: string,
    config?: any
  ): Promise<{ success: boolean; agent: any }> =>
    fetchWithAuth(
      `/v1/agents/company/${companyId}/activate/${agentTemplateId}`,
      {
        method: "POST",
        body: JSON.stringify(config || {}),
      }
    ),

  // Update company agent
  updateCompanyAgent: (
    companyId: string,
    agentId: string,
    updates: any
  ): Promise<{ success: boolean; agent: any }> =>
    fetchWithAuth(`/v1/agents/company/${companyId}/agents/${agentId}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    }),

  // Toggle agent status
  toggleAgentStatus: (
    companyId: string,
    agentId: string,
    isActive: boolean
  ): Promise<{ success: boolean; agent: any }> =>
    fetchWithAuth(`/v1/agents/company/${companyId}/agents/${agentId}/toggle`, {
      method: "PUT",
      body: JSON.stringify({ is_active: isActive }),
    }),

  // Voice options
  getVoiceOptions: (): Promise<{ voices: VoiceOption[]; total: number }> =>
    fetchWithAuth("/v1/voices/"),

  // Integration providers
  getIntegrationProviders: (
    category?: string
  ): Promise<{ providers: any[]; total: number }> =>
    fetchWithAuth(
      `/v1/agents/integrations${category ? `?category=${category}` : ""}`
    ),

  // Get agent integrations
  getAgentIntegrations: (
    companyId: string,
    agentId: string
  ): Promise<{ success: boolean; integrations: any }> =>
    fetchWithAuth(
      `/v1/agents/company/${companyId}/agents/${agentId}/integrations`
    ),

  // Legacy endpoints for backward compatibility
  getBusinessCategories: (): Promise<{ categories: BusinessCategory[] }> =>
    fetchWithAuth("/agents/categories"),

  getAdminStats: (): Promise<AdminStats> =>
    fetchWithAuth("/agents/admin/stats"),
};

export type { ApiError };
