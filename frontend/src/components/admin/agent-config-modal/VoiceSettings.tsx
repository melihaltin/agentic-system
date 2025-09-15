import { LANGUAGE_OPTIONS } from "@/features/admin/constants/agent-types";
import { isVoiceSettings } from "@/features/admin/utils/agent-helpers";
import { AgentType } from "@/types/admin.types";

export const VoiceSettings = ({
  agent,
  formData,
  onChange,
  voiceOptions,
  isLoadingVoices,
  onPlayPreview,
}: {
  agent: AgentType;
  formData: AgentType;
  onChange: (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => void;
  voiceOptions: any[];
  isLoadingVoices: boolean;
  onPlayPreview: (url: string) => void;
}) => {
  const voiceSettings = isVoiceSettings(formData.settings)
    ? formData.settings
    : null;

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          name="language"
          value={formData.settings.language}
          onChange={onChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {LANGUAGE_OPTIONS.map((language) => (
            <option key={language} value={language}>
              {language}
            </option>
          ))}
        </select>
      </div>

      {voiceSettings && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Voice Selection
          </label>
          {isLoadingVoices ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-3">
              {voiceOptions.map((voice) => (
                <div
                  key={voice.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    voiceSettings.voice?.id === voice.id
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() =>
                    onChange({
                      target: { name: "voice", value: voice.id },
                    } as any)
                  }
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        name="voiceRadio"
                        value={voice.id}
                        checked={voiceSettings.voice?.id === voice.id}
                        onChange={() => {}}
                        className="text-blue-600"
                      />
                      <div>
                        <p className="font-medium text-gray-900">
                          {voice.name}
                        </p>
                        <p className="text-sm text-gray-600">
                          {voice.language} • {voice.gender}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onPlayPreview(voice.preview);
                      }}
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      Preview
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
