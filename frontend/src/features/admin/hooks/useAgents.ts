import { useState, useEffect } from 'react';
import { AgentType } from '@/types/admin.types';
import { AgentService } from '../services/agent-service';

export const useAgents = (businessCategory: string) => {
  const [agents, setAgents] = useState<AgentType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAgents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const agentData = await AgentService.loadAgents(businessCategory);
      setAgents(agentData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAgent = async (agentId: string, isActive: boolean) => {
    try {
      const updatedAgent = await AgentService.toggleAgentStatus(agentId, isActive);
      if (updatedAgent) {
        setAgents(prev => 
          prev.map(agent => 
            agent.id === agentId ? updatedAgent : agent
          )
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update agent');
    }
  };

  const updateAgent = async (updatedAgent: AgentType) => {
    try {
      const result = await AgentService.updateAgentSettings(updatedAgent.id, updatedAgent.settings);
      if (result) {
        setAgents(prev => 
          prev.map(agent => 
            agent.id === updatedAgent.id ? result : agent
          )
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update agent');
    }
  };

  useEffect(() => {
    loadAgents();
  }, [businessCategory]);

  // Computed values
  const activeAgentsCount = agents.filter(agent => agent.isActive).length;
  const totalAgentsCount = agents.length;

  return {
    agents,
    isLoading,
    error,
    activeAgentsCount,
    totalAgentsCount,
    toggleAgent,
    updateAgent,
    refetch: loadAgents,
  };
};
