import React from "react";
import { VoiceOption } from "@/types/admin.types";
import VoiceSelector from "./VoiceSelector";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import LanguageSelector from "./LanguageSelector";

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

  const handleLanguageChange = (value: string) => {
    onChange({
      target: { name: "language", value, type: "select" },
    });
  };

  const handleCustomPromptChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    onChange(e);
  };

  return (
    <div className="space-y-6">
      {/* Voice Selector */}
      <VoiceSelector
        selectedVoice={voiceSettings?.voice}
        onVoiceSelect={handleVoiceSelect}
      />

      {/* Language Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <Label htmlFor="language" className="text-sm font-medium">
            Language
          </Label>
          <LanguageSelector
            value={voiceSettings?.language || "en-US"}
            onValueChange={handleLanguageChange}
            placeholder="Select a language"
          />
        </div>
      </div>

      {/* Custom Prompt */}
      <div className="space-y-2">
        <Label htmlFor="customPrompt" className="text-sm font-medium">
          Custom Prompt
        </Label>
        <Textarea
          id="customPrompt"
          name="customPrompt"
          value={voiceSettings?.customPrompt || ""}
          onChange={handleCustomPromptChange}
          rows={4}
          placeholder="Enter custom instructions for this agent..."
          className="resize-none"
        />
        <p className="text-sm text-muted-foreground">
          Provide specific instructions to customize how this agent should
          behave.
        </p>
      </div>
    </div>
  );
};

export default VoiceSettings;
