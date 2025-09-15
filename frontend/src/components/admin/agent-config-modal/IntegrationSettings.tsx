import {
  ECOMMERCE_PLATFORMS,
  CAR_RENTAL_PLATFORMS,
  PLATFORM_FIELDS,
} from "@/features/admin/constants/agent-types";
import { AgentType } from "@/types/admin.types";

export const IntegrationSettings = ({
  agent,
  selectedPlatform,
  platformConfig,
  onChange,
}: {
  agent: AgentType;
  selectedPlatform: string;
  platformConfig: Record<string, string>;
  onChange: (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => void;
}) => {
  // Determine available platforms based on agent category
  const availablePlatforms =
    agent.category === "ecommerce" ? ECOMMERCE_PLATFORMS : CAR_RENTAL_PLATFORMS;
  const selectedPlatformFields = selectedPlatform
    ? PLATFORM_FIELDS[selectedPlatform as keyof typeof PLATFORM_FIELDS]
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Platform Integration
        </h3>
        <p className="text-gray-600 mb-6">
          Select and configure your {agent.category} platform integration.
        </p>
      </div>

      {/* Platform Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Platform
        </label>
        <select
          name="platform"
          value={selectedPlatform}
          onChange={onChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Select a platform...</option>
          {availablePlatforms.map((platform) => (
            <option key={platform.id} value={platform.id}>
              {platform.name}
            </option>
          ))}
        </select>
        {selectedPlatform && (
          <p className="text-sm text-gray-500 mt-1">
            {
              availablePlatforms.find((p) => p.id === selectedPlatform)
                ?.description
            }
          </p>
        )}
      </div>

      {/* Platform Configuration Fields */}
      {selectedPlatform && selectedPlatformFields && (
        <div className="border-t pt-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">
            {availablePlatforms.find((p) => p.id === selectedPlatform)?.name}{" "}
            Configuration
          </h4>
          <div className="space-y-4">
            {selectedPlatformFields.map((field) => (
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
                  name={`platform_${field.id}`}
                  value={platformConfig[field.id] || ""}
                  onChange={onChange}
                  placeholder={field.placeholder}
                  required={field.required}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connection Status */}
      {selectedPlatform && Object.keys(platformConfig).length > 0 && (
        <div className="border-t pt-6">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-gray-400 rounded-full mr-3"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Connection Status
                </p>
                <p className="text-xs text-gray-500">
                  Configuration saved - test connection after saving
                </p>
              </div>
            </div>
            <button
              type="button"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Test Connection
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
