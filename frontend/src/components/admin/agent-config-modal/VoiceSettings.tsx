import { isVoiceSettings } from "@/features/admin/utils/agent-helpers";
import { AgentType, VoiceOption } from "@/types/admin.types";
import VoiceSelector from "./VoiceSelector";

export const VoiceSettings = ({
  agent,
  formData,
  onChange,
  onVoiceSelect,
}: {
  agent: AgentType;
  formData: AgentType;
  onChange: (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => void;
  onVoiceSelect?: (voice: VoiceOption) => void;
}) => {
  const voiceSettings = isVoiceSettings(formData.settings)
    ? formData.settings
    : null;

  const handleVoiceSelect = (voice: VoiceOption) => {
    if (onVoiceSelect) {
      onVoiceSelect(voice);
    } else {
      // Fallback: Simulate the onChange event for compatibility
      onChange({
        target: { name: "voice", value: voice.id, type: "select" },
      } as any);
    }
  };

  return (
    <div className="space-y-6">
      {voiceSettings && (
        <div>
          <VoiceSelector
            selectedVoice={voiceSettings.voice}
            onVoiceSelect={handleVoiceSelect}
            className="space-y-4"
          />
        </div>
      )}

      {voiceSettings && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Personality Setting */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Personality
            </label>
            <select
              name="personality"
              value={voiceSettings.personality || ""}
              onChange={onChange}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select personality</option>
              <option value="friendly">Friendly</option>
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="enthusiastic">Enthusiastic</option>
              <option value="calm">Calm</option>
            </select>
          </div>

          {/* Response Speed */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Response Speed
            </label>
            <select
              name="responseSpeed"
              value={voiceSettings.responseSpeed || "normal"}
              onChange={onChange}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="fast">Fast</option>
              <option value="normal">Normal</option>
              <option value="slow">Slow</option>
            </select>
          </div>

          {/* Max Session Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Session Duration (minutes)
            </label>
            <input
              type="number"
              name="maxSessionDuration"
              value={voiceSettings.maxSessionDuration || 30}
              onChange={onChange}
              min="1"
              max="120"
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Language */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              name="language"
              value={voiceSettings.language || "tr-TR"}
              onChange={onChange}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="tr-TR">Turkish</option>
              <option value="en-US">English (US)</option>
              <option value="en-GB">English (UK)</option>
            </select>
          </div>
        </div>
      )}

      {voiceSettings && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Prompt
          </label>
          <textarea
            name="customPrompt"
            value={voiceSettings.customPrompt || ""}
            onChange={onChange}
            rows={4}
            placeholder="Enter custom instructions for this agent..."
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="mt-1 text-sm text-gray-500">
            Provide specific instructions to customize how this agent should
            behave and respond to customers.
          </p>
        </div>
      )}
    </div>
  );
};
