"use client";

import React from "react";
import { AgentType } from "@/types/admin.types";
import {
  isVoiceAgent,
  getAgentTypeDisplayName,
} from "@/features/admin/utils/agent-helpers";

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
    <div
      className={`bg-white rounded-xl shadow-sm border transition-all duration-200 hover:shadow-md ${
        agent.isActive
          ? "border-green-200 ring-2 ring-green-100"
          : "border-gray-200"
      }`}
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div
              className={`w-16 h-16 rounded-xl flex items-center justify-center text-white ${agent.color}`}
            >
              <AgentIcon iconName={agent.icon} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {agent.name}
              </h3>
              <p className="text-sm text-gray-600 mt-1">{agent.description}</p>
              <div className="flex items-center mt-2 space-x-4">
                <span className="text-xs text-gray-500">
                  {getAgentTypeDisplayName(agent.communicationType)}
                </span>
                <span className="text-xs text-gray-500">
                  Last updated:{" "}
                  {new Date(agent.lastUpdated).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
          <StatusBadge isActive={agent.isActive} />
        </div>
      </div>

      {/* Settings Preview */}
      <AgentSettingsPreview agent={agent} />

      {/* Integration Status */}
      {agent.requiredIntegrations.length > 0 && (
        <IntegrationStatus agent={agent} />
      )}

      {/* Actions */}
      <div className="p-6 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <ToggleSwitch
            isActive={agent.isActive}
            onToggle={handleToggle}
            isLoading={isLoading}
          />
          <button
            onClick={() => onConfigure(agent)}
            className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            Configure
          </button>
        </div>
      </div>
    </div>
  );
};

// Sub-components for better organization
const AgentIcon = ({ iconName }: { iconName: string }) => {
  const iconMap = {
    "shopping-cart": (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.5 4H19M7 13v8a2 2 0 002 2h8a2 2 0 002-2v-8M9 9h6"
        />
      </svg>
    ),
    car: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"
        />
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 6H5l2-5h6l2 5zm-8 11V9h10v8H5z"
        />
      </svg>
    ),
    support: (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M12 2.458V6.42M21.542 12H17.58M12 21.542V17.58M6.42 12H2.458"
        />
      </svg>
    ),
  };

  return (
    iconMap[iconName as keyof typeof iconMap] || (
      <svg
        className="w-8 h-8"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        />
      </svg>
    )
  );
};

const StatusBadge = ({ isActive }: { isActive: boolean }) => (
  <span
    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
      isActive ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
    }`}
  >
    <div
      className={`w-2 h-2 rounded-full mr-1.5 ${
        isActive ? "bg-green-500" : "bg-gray-400"
      }`}
    />
    {isActive ? "Active" : "Inactive"}
  </span>
);

const AgentSettingsPreview = ({ agent }: { agent: AgentType }) => (
  <div className="p-6 bg-gray-50">
    <div className="grid grid-cols-2 gap-4 text-sm">
      <div>
        <span className="font-medium text-gray-700">Custom Name:</span>
        <p className="text-gray-600 mt-1">{agent.settings.customName}</p>
      </div>
      {isVoiceAgent(agent) &&
        "voice" in agent.settings &&
        agent.settings.voice && (
          <div>
            <span className="font-medium text-gray-700">Voice:</span>
            <p className="text-gray-600 mt-1">{agent.settings.voice.name}</p>
          </div>
        )}
      <div>
        <span className="font-medium text-gray-700">Language:</span>
        <p className="text-gray-600 mt-1">{agent.settings.language}</p>
      </div>
      <div>
        <span className="font-medium text-gray-700">Integrations:</span>
        <p className="text-gray-600 mt-1">
          {agent.requiredIntegrations.length} required
        </p>
      </div>
    </div>
  </div>
);

const IntegrationStatus = ({ agent }: { agent: AgentType }) => (
  <div className="px-6 pb-4 bg-gray-50 border-t border-gray-200">
    <span className="text-xs font-medium text-gray-700 uppercase tracking-wide">
      Required Integrations
    </span>
    <div className="mt-2 flex flex-wrap gap-2">
      {agent.requiredIntegrations.map((integration) => {
        const isConfigured = Object.keys(
          agent.settings.integrationConfigs
        ).includes(integration.id);
        return (
          <span
            key={integration.id}
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              isConfigured
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {integration.name}
            {isConfigured ? (
              <svg
                className="ml-1 w-3 h-3"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg
                className="ml-1 w-3 h-3"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </span>
        );
      })}
    </div>
  </div>
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
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        isActive ? "bg-green-600" : "bg-gray-200"
      } ${isLoading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
      aria-label={isActive ? "Deactivate agent" : "Activate agent"}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          isActive ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
    <span className="text-sm font-medium text-gray-700">
      {isActive ? "Deactivate" : "Activate"}
    </span>
  </div>
);

export default AgentCard;
