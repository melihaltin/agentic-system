"use client";

import React, { useState } from "react";
import { AgentType } from "@/types/admin.types";
import { useAgents } from "@/features/admin/hooks/useAgents";
import AgentCard from "./AgentCard";

import { FiUsers, FiCheckCircle, FiTrendingUp, FiRewind } from "react-icons/fi";
import AgentConfigModal from "./agent-config-modal/AgentConfigModal";
import { useAuthStore } from "@/store/auth";

const MyAgentsPage: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<AgentType | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const businessCategory = useAuthStore(
    (state) => state.profile?.company?.business_category
  );

  const {
    agents,
    isLoading,
    error,
    activeAgentsCount,
    totalAgentsCount,
    toggleAgent,
    updateAgent,
    activateAgent,
  } = useAgents(businessCategory);

  const handleConfigureAgent = (agent: AgentType) => {
    setSelectedAgent(agent);
    setIsModalOpen(true);
  };

  const handleActivateAgent = (agent: AgentType) => {
    // Activate edilecek agent için modal'ı aç
    setSelectedAgent(agent);
    setIsModalOpen(true);
  };

  const handleSaveAgentConfig = async (updatedAgent: AgentType) => {
    try {
      if (!selectedAgent?.isActive && selectedAgent?.isCompanyAgent === false) {
        // Activate new agent with configuration
        const templateId = selectedAgent?.agentTemplateId || selectedAgent?.id;

        const config = {
          custom_name: updatedAgent.settings.customName,
          custom_prompt: updatedAgent.settings.customPrompt,
          integrationConfigs: updatedAgent.settings.integrationConfigs || {},
          configuration: {},
          ...((updatedAgent.settings as any).voice && {
            selected_voice_id: (updatedAgent.settings as any).voice.id,
          }),
        };

        await activateAgent(templateId, config);
      } else {
        // Update existing active agent
        await updateAgent(updatedAgent);
      }
    } catch (error) {
      console.error("Error saving agent config:", error);
    } finally {
      setIsModalOpen(false);
      setSelectedAgent(null);
    }
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedAgent(null);
  };

  // Ajanları doğrudan kullan, filtrelemeye gerek yok
  const displayedAgents = agents;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          <span className="text-gray-600 font-medium">Loading agents...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50/30 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-gray-100 p-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                AI Agent Management
              </h1>
              <p className="text-gray-600 text-lg">
                Configure and manage your AI agents with ease
              </p>
            </div>
            {/* Arama çubuğu kaldırıldı */}
          </div>

          {/* Stats */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard
              icon={<FiUsers className="w-6 h-6" />}
              title="Total Agents"
              value={totalAgentsCount}
              color="blue"
            />
            <StatCard
              icon={<FiCheckCircle className="w-6 h-6" />}
              title="Active Agents"
              value={activeAgentsCount}
              color="emerald"
            />
            <StatCard
              icon={<FiTrendingUp className="w-6 h-6" />}
              title="Performance"
              value="94.5%"
              color="purple"
            />
          </div>
        </div>

        {/* Agents Grid */}
        {displayedAgents.length === 0 ? (
          <div className="bg-white rounded-2xl border border-gray-100 p-16 text-center">
            <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <FiRewind className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No agents found
            </h3>
            <p className="text-gray-500 text-lg">
              You haven't created any agents yet.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {displayedAgents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onToggle={toggleAgent}
                onConfigure={handleConfigureAgent}
                onActivate={handleActivateAgent}
              />
            ))}
          </div>
        )}

        {/* Modal */}
        {selectedAgent && (
          <AgentConfigModal
            isOpen={isModalOpen}
            onClose={handleModalClose}
            agent={selectedAgent}
            onSave={handleSaveAgentConfig}
          />
        )}
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({
  icon,
  title,
  value,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  color: "blue" | "emerald" | "purple";
}) => {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-600 border-blue-100",
    emerald: "bg-emerald-50 text-emerald-600 border-emerald-100",
    purple: "bg-purple-50 text-purple-600 border-purple-100",
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center">
        <div className={`p-3 rounded-xl border ${colorClasses[color]}`}>
          {icon}
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
      </div>
    </div>
  );
};

export default MyAgentsPage;
