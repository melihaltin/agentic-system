"use client";

import React from "react";
import { AgentType } from "@/types/admin.types";
import {
  isVoiceAgent,
  getAgentTypeDisplayName,
} from "@/features/admin/utils/agent-helpers";
import {
  FiShoppingCart,
  FiHeadphones,
  FiMonitor,
  FiCheck,
  FiX,
  FiSettings,
  FiCamera,
} from "react-icons/fi";

interface AgentCardProps {
  agent: AgentType;
  onToggle: (agentId: string, isActive: boolean) => void;
  onConfigure: (agent: AgentType) => void;
  isLoading?: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onToggle,
  onConfigure,
  isLoading = false,
}) => {
  const handleToggle = () => {
    onToggle(agent.id, !agent.isActive);
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 hover:border-gray-200 transition-all duration-300 hover:shadow-lg group">
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div
              className={`w-14 h-14 rounded-xl ${agent.color} flex items-center justify-center shadow-sm`}
            >
              <AgentIcon iconName={agent.icon} />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {agent.name}
              </h3>
              <p className="text-sm text-gray-500 leading-relaxed">
                {agent.description}
              </p>
            </div>
          </div>
          <StatusBadge isActive={agent.isActive} />
        </div>

        <div className="flex items-center space-x-6 text-xs text-gray-400">
          <span className="font-medium">
            {getAgentTypeDisplayName(agent.communicationType)}
          </span>
          <span>
            Updated {new Date(agent.lastUpdated).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Settings Preview */}
      <div className="px-6 py-4 bg-gray-50/50">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">
              Custom Name
            </p>
            <p className="text-sm text-gray-900">{agent.settings.customName}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">Language</p>
            <p className="text-sm text-gray-900">{agent.settings.language}</p>
          </div>
          {isVoiceAgent(agent) &&
            "voice" in agent.settings &&
            agent.settings.voice && (
              <div>
                <p className="text-xs font-medium text-gray-600 mb-1">Voice</p>
                <p className="text-sm text-gray-900">
                  {agent.settings.voice.name}
                </p>
              </div>
            )}
          <div>
            <p className="text-xs font-medium text-gray-600 mb-1">
              Integrations
            </p>
            <p className="text-sm text-gray-900">
              {agent.requiredIntegrations.length} configured
            </p>
          </div>
        </div>
      </div>

      {/* Integration Status */}
      {agent.requiredIntegrations.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-100">
          <p className="text-xs font-semibold text-gray-600 mb-3 uppercase tracking-wide">
            Integrations
          </p>
          <div className="flex flex-wrap gap-2">
            {agent.requiredIntegrations.map((integration) => {
              const isConfigured = Object.keys(
                agent.settings.integrationConfigs
              ).includes(integration.id);
              return (
                <span
                  key={integration.id}
                  className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium ${
                    isConfigured
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                      : "bg-rose-50 text-rose-700 border border-rose-200"
                  }`}
                >
                  {integration.name}
                  {isConfigured ? (
                    <FiCheck className="ml-1.5 w-3 h-3" />
                  ) : (
                    <FiX className="ml-1.5 w-3 h-3" />
                  )}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="p-6 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <ToggleSwitch
            isActive={agent.isActive}
            onToggle={handleToggle}
            isLoading={isLoading}
          />
          <button
            onClick={() => onConfigure(agent)}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors group-hover:bg-blue-100"
          >
            <FiSettings className="w-4 h-4 mr-2" />
            Configure
          </button>
        </div>
      </div>
    </div>
  );
};

// Sub-components
const AgentIcon = ({ iconName }: { iconName: string }) => {
  const iconMap = {
    "shopping-cart": <FiShoppingCart className="w-7 h-7 text-white" />,
    car: <FiCamera className="w-7 h-7 text-white" />,
    support: <FiHeadphones className="w-7 h-7 text-white" />,
  };

  return (
    iconMap[iconName as keyof typeof iconMap] || (
      <FiMonitor className="w-7 h-7 text-white" />
    )
  );
};

const StatusBadge = ({ isActive }: { isActive: boolean }) => (
  <span
    className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium ${
      isActive
        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
        : "bg-gray-50 text-gray-600 border border-gray-200"
    }`}
  >
    <div
      className={`w-2 h-2 rounded-full mr-2 ${
        isActive ? "bg-emerald-500" : "bg-gray-400"
      }`}
    />
    {isActive ? "Active" : "Inactive"}
  </span>
);

const ToggleSwitch = ({
  isActive,
  onToggle,
  isLoading,
}: {
  isActive: boolean;
  onToggle: () => void;
  isLoading: boolean;
}) => (
  <div className="flex items-center space-x-3">
    <button
      onClick={onToggle}
      disabled={isLoading}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        isActive ? "bg-emerald-500" : "bg-gray-200"
      } ${isLoading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${
          isActive ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
    <span className="text-sm font-medium text-gray-700">
      {isActive ? "Active" : "Inactive"}
    </span>
  </div>
);

export default AgentCard;
