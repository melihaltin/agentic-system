import { RESPONSE_SPEED_OPTIONS, RESPONSE_STYLE_OPTIONS } from "@/features/admin/constants/agent-types";
import { isChatSettings, isVoiceAgent, isVoiceSettings } from "@/features/admin/utils/agent-helpers";
import { AgentType } from "@/types/admin.types";

export const GeneralSettings = ({
  agent,
  formData,
  onChange,
}: {
  agent: AgentType;
  formData: AgentType;
  onChange: (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => void;
}) => {
  const voiceSettings = isVoiceSettings(formData.settings)
    ? formData.settings
    : null;
  const chatSettings = isChatSettings(formData.settings)
    ? formData.settings
    : null;

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Custom Agent Name
        </label>
        <input
          type="text"
          name="customName"
          value={formData.settings.customName}
          onChange={onChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter custom name for your agent"
        />
      </div>

      {/* Show response style for chat agents */}
      {!isVoiceAgent(agent) && chatSettings && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Response Style
          </label>
          <select
            name="responseStyle"
            value={chatSettings.responseStyle || "conversational"}
            onChange={onChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {RESPONSE_STYLE_OPTIONS.map((style) => (
              <option key={style.value} value={style.value}>
                {style.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Only show response speed and max session for voice agents */}
      {isVoiceAgent(agent) && voiceSettings && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Response Speed
            </label>
            <select
              name="responseSpeed"
              value={voiceSettings.responseSpeed}
              onChange={onChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {RESPONSE_SPEED_OPTIONS.map((speed) => (
                <option key={speed.value} value={speed.value}>
                  {speed.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Session Duration (minutes)
            </label>
            <input
              type="number"
              name="maxSessionDuration"
              value={voiceSettings.maxSessionDuration}
              onChange={onChange}
              min="5"
              max="120"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </>
      )}
    </div>
  );
};
