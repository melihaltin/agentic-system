import { VoiceOption } from "@/types/admin.types";
import VoiceSelector from "./VoiceSelector";

interface VoiceSettingsProps {
  formData: {
    settings: {
      voice?: VoiceOption;
      language?: string;
      customPrompt?: string;
    };
  };
  onChange: (e: any) => void;
  onVoiceSelect?: (voice: VoiceOption) => void;
}

export const VoiceSettings: React.FC<VoiceSettingsProps> = ({
  formData,
  onChange,
  onVoiceSelect,
}) => {
  const voiceSettings = formData.settings;

  const handleVoiceSelect = (voice: VoiceOption) => {
    if (onVoiceSelect) {
      onVoiceSelect(voice);
    } else {
      onChange({
        target: { name: "voice", value: voice.id, type: "select" },
      });
    }
  };

  return (
    <div className="space-y-6">
      <VoiceSelector
        selectedVoice={voiceSettings?.voice}
        onVoiceSelect={handleVoiceSelect}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Language
          </label>
          <select
            name="language"
            value={voiceSettings?.language || "tr-TR"}
            onChange={onChange}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-gray-400"
          >
            <option value="tr-TR">Turkish</option>
            <option value="en-US">English (US)</option>
            <option value="en-GB">English (UK)</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Custom Prompt
        </label>
        <textarea
          name="customPrompt"
          value={voiceSettings?.customPrompt || ""}
          onChange={onChange}
          rows={4}
          placeholder="Enter custom instructions for this agent..."
          className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-gray-400 resize-none"
        />
        <p className="mt-1 text-sm text-gray-500">
          Provide specific instructions to customize how this agent should
          behave.
        </p>
      </div>
    </div>
  );
};

export default VoiceSelector;
