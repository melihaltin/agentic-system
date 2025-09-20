import {
  ECOMMERCE_PLATFORMS,
  CAR_RENTAL_PLATFORMS,
  PLATFORM_FIELDS,
} from "@/features/admin/constants/agent-types";
import { AgentType } from "@/types/admin.types";
import { useState } from "react";
import { Plus, Trash2, Settings } from "lucide-react";

interface IntegrationConfig {
  platform: string;
  config: Record<string, string>;
}

interface IntegrationSettingsProps {
  agent: AgentType;
  selectedPlatform: string;
  platformConfig: Record<string, string>;
  onChange: (e: any) => void;
}

export const IntegrationSettings = ({
  agent,
  selectedPlatform,
  platformConfig,
  onChange,
}: IntegrationSettingsProps) => {
  // Determine available platforms based on agent category
  const availablePlatforms =
    agent.category === "ecommerce" ? ECOMMERCE_PLATFORMS : CAR_RENTAL_PLATFORMS;

  // Get existing integrations from agent settings
  const existingIntegrations = agent.settings.integrationConfigs || {};

  // State for managing multiple integrations
  const [integrations, setIntegrations] = useState<IntegrationConfig[]>(() => {
    return Object.keys(existingIntegrations)
      .filter(
        (key) =>
          key &&
          existingIntegrations[key] &&
          Object.keys(existingIntegrations[key]).length > 0
      )
      .map((platform) => ({
        platform,
        config: existingIntegrations[platform] || {},
      }));
  });

  const [editingIntegration, setEditingIntegration] = useState<string | null>(
    null
  );

  // Helper functions
  const addIntegration = (platformId: string) => {
    const newIntegration: IntegrationConfig = {
      platform: platformId,
      config: {},
    };
    setIntegrations([...integrations, newIntegration]);
    setEditingIntegration(platformId);
  };

  const removeIntegration = (platformId: string) => {
    setIntegrations(integrations.filter((int) => int.platform !== platformId));
    if (editingIntegration === platformId) {
      setEditingIntegration(null);
    }

    // Also update the agent settings to remove this integration
    const updatedConfigs = { ...existingIntegrations };
    delete updatedConfigs[platformId];

    // Trigger onChange to update the parent component
    onChange({
      target: {
        name: "integrationConfigs",
        value: updatedConfigs,
        type: "object",
      },
    } as any);
  };

  const updateIntegrationConfig = (
    platformId: string,
    field: string,
    value: string
  ) => {
    setIntegrations(
      integrations.map((int) => {
        if (int.platform === platformId) {
          const updatedConfig = { ...int.config, [field]: value };

          // Also update the agent settings
          const updatedConfigs = {
            ...existingIntegrations,
            [platformId]: updatedConfig,
          };

          // Trigger onChange to update the parent component
          setTimeout(() => {
            onChange({
              target: {
                name: "integrationConfigs",
                value: updatedConfigs,
                type: "object",
              },
            } as any);
          }, 0);

          return { ...int, config: updatedConfig };
        }
        return int;
      })
    );
  };

  const getAvailablePlatforms = () => {
    const configuredPlatforms = integrations.map((int) => int.platform);
    return availablePlatforms.filter(
      (platform) => !configuredPlatforms.includes(platform.id)
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Platform Integrations
        </h3>
        <p className="text-gray-600 mb-6">
          Configure multiple platform integrations for your {agent.category}{" "}
          agent.
        </p>
      </div>

      {/* Existing Integrations */}
      {integrations.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">
            Configured Integrations ({integrations.length})
          </h4>
          {integrations.map((integration) => {
            const platform = availablePlatforms.find(
              (p) => p.id === integration.platform
            );
            const isEditing = editingIntegration === integration.platform;
            const platformFields =
              PLATFORM_FIELDS[
                integration.platform as keyof typeof PLATFORM_FIELDS
              ] || [];

            return (
              <div
                key={integration.platform}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <h5 className="font-medium text-gray-900">
                      {platform?.name}
                    </h5>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {Object.keys(integration.config).length} fields configured
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setEditingIntegration(
                          isEditing ? null : integration.platform
                        )
                      }
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <Settings className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => removeIntegration(integration.platform)}
                      className="p-1 text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {isEditing && (
                  <div className="space-y-4 pt-3 border-t border-gray-100">
                    <p className="text-sm text-gray-600">
                      {platform?.description}
                    </p>
                    {platformFields.map((field: any) => (
                      <div key={field.id}>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {field.name}
                          {field.required && (
                            <span className="text-red-500 ml-1">*</span>
                          )}
                        </label>
                        <input
                          type={
                            field.type === "password"
                              ? "password"
                              : field.type === "url"
                              ? "url"
                              : "text"
                          }
                          value={integration.config[field.id] || ""}
                          onChange={(e) =>
                            updateIntegrationConfig(
                              integration.platform,
                              field.id,
                              e.target.value
                            )
                          }
                          placeholder={field.placeholder}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Add New Integration */}
      {getAvailablePlatforms().length > 0 && (
        <div className="border-2 border-dashed border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <Plus className="mx-auto h-8 w-8 text-gray-400 mb-3" />
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Add Integration
            </h4>
            <p className="text-sm text-gray-500 mb-4">
              Connect to additional platforms
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {getAvailablePlatforms().map((platform) => (
                <button
                  key={platform.id}
                  type="button"
                  onClick={() => addIntegration(platform.id)}
                  className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors"
                >
                  {platform.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* No Integrations State */}
      {integrations.length === 0 && (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <Settings className="mx-auto h-8 w-8 text-gray-400 mb-3" />
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            No Integrations Configured
          </h4>
          <p className="text-sm text-gray-500 mb-4">
            Add your first platform integration to get started
          </p>
          <div className="flex flex-wrap gap-2 justify-center">
            {availablePlatforms.map((platform) => (
              <button
                key={platform.id}
                type="button"
                onClick={() => addIntegration(platform.id)}
                className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors"
              >
                {platform.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
