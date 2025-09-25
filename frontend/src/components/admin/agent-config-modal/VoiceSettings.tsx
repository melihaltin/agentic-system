import React from "react";
import { VoiceOption } from "@/types/admin.types";
import VoiceSelector from "./VoiceSelector";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui";
import {
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/Select";

// Dünya dillerinin kapsamlı listesi
const WORLD_LANGUAGES = [
  { code: "af-ZA", name: "Afrikaans", nativeName: "Afrikaans" },
  { code: "sq-AL", name: "Albanian", nativeName: "Shqip" },
  { code: "am-ET", name: "Amharic", nativeName: "አማርኛ" },
  { code: "ar-SA", name: "Arabic", nativeName: "العربية" },
  { code: "hy-AM", name: "Armenian", nativeName: "Հայերեն" },
  { code: "az-AZ", name: "Azerbaijani", nativeName: "Azərbaycan" },
  { code: "eu-ES", name: "Basque", nativeName: "Euskera" },
  { code: "be-BY", name: "Belarusian", nativeName: "Беларуская" },
  { code: "bn-BD", name: "Bengali", nativeName: "বাংলা" },
  { code: "bs-BA", name: "Bosnian", nativeName: "Bosanski" },
  { code: "bg-BG", name: "Bulgarian", nativeName: "Български" },
  { code: "my-MM", name: "Burmese", nativeName: "မြန်မာ" },
  { code: "ca-ES", name: "Catalan", nativeName: "Català" },
  { code: "zh-CN", name: "Chinese (Simplified)", nativeName: "简体中文" },
  { code: "zh-TW", name: "Chinese (Traditional)", nativeName: "繁體中文" },
  { code: "hr-HR", name: "Croatian", nativeName: "Hrvatski" },
  { code: "cs-CZ", name: "Czech", nativeName: "Čeština" },
  { code: "da-DK", name: "Danish", nativeName: "Dansk" },
  { code: "nl-NL", name: "Dutch", nativeName: "Nederlands" },
  { code: "en-US", name: "English (US)", nativeName: "English (US)" },
  { code: "en-GB", name: "English (UK)", nativeName: "English (UK)" },
  { code: "en-AU", name: "English (Australia)", nativeName: "English (AU)" },
  { code: "en-CA", name: "English (Canada)", nativeName: "English (CA)" },
  { code: "et-EE", name: "Estonian", nativeName: "Eesti" },
  { code: "fi-FI", name: "Finnish", nativeName: "Suomi" },
  { code: "fr-FR", name: "French", nativeName: "Français" },
  { code: "fr-CA", name: "French (Canada)", nativeName: "Français (CA)" },
  { code: "gl-ES", name: "Galician", nativeName: "Galego" },
  { code: "ka-GE", name: "Georgian", nativeName: "ქართული" },
  { code: "de-DE", name: "German", nativeName: "Deutsch" },
  { code: "el-GR", name: "Greek", nativeName: "Ελληνικά" },
  { code: "gu-IN", name: "Gujarati", nativeName: "ગુજરાતી" },
  { code: "he-IL", name: "Hebrew", nativeName: "עברית" },
  { code: "hi-IN", name: "Hindi", nativeName: "हिन्दी" },
  { code: "hu-HU", name: "Hungarian", nativeName: "Magyar" },
  { code: "is-IS", name: "Icelandic", nativeName: "Íslenska" },
  { code: "id-ID", name: "Indonesian", nativeName: "Bahasa Indonesia" },
  { code: "ga-IE", name: "Irish", nativeName: "Gaeilge" },
  { code: "it-IT", name: "Italian", nativeName: "Italiano" },
  { code: "ja-JP", name: "Japanese", nativeName: "日本語" },
  { code: "kn-IN", name: "Kannada", nativeName: "ಕನ್ನಡ" },
  { code: "kk-KZ", name: "Kazakh", nativeName: "Қазақ тілі" },
  { code: "km-KH", name: "Khmer", nativeName: "ខ្មែរ" },
  { code: "ko-KR", name: "Korean", nativeName: "한국어" },
  { code: "ku-TR", name: "Kurdish", nativeName: "Kurdî" },
  { code: "ky-KG", name: "Kyrgyz", nativeName: "Кыргызча" },
  { code: "lo-LA", name: "Lao", nativeName: "ລາວ" },
  { code: "lv-LV", name: "Latvian", nativeName: "Latviešu" },
  { code: "lt-LT", name: "Lithuanian", nativeName: "Lietuvių" },
  { code: "mk-MK", name: "Macedonian", nativeName: "Македонски" },
  { code: "ms-MY", name: "Malay", nativeName: "Bahasa Melayu" },
  { code: "ml-IN", name: "Malayalam", nativeName: "മലയാളം" },
  { code: "mt-MT", name: "Maltese", nativeName: "Malti" },
  { code: "mr-IN", name: "Marathi", nativeName: "मराठी" },
  { code: "mn-MN", name: "Mongolian", nativeName: "Монгол" },
  { code: "ne-NP", name: "Nepali", nativeName: "नेपाली" },
  { code: "no-NO", name: "Norwegian", nativeName: "Norsk" },
  { code: "or-IN", name: "Odia", nativeName: "ଓଡ଼ିଆ" },
  { code: "ps-AF", name: "Pashto", nativeName: "پښتو" },
  { code: "fa-IR", name: "Persian", nativeName: "فارسی" },
  { code: "pl-PL", name: "Polish", nativeName: "Polski" },
  { code: "pt-PT", name: "Portuguese", nativeName: "Português" },
  { code: "pt-BR", name: "Portuguese (Brazil)", nativeName: "Português (BR)" },
  { code: "pa-IN", name: "Punjabi", nativeName: "ਪੰਜਾਬੀ" },
  { code: "ro-RO", name: "Romanian", nativeName: "Română" },
  { code: "ru-RU", name: "Russian", nativeName: "Русский" },
  { code: "sr-RS", name: "Serbian", nativeName: "Српски" },
  { code: "si-LK", name: "Sinhala", nativeName: "සිංහල" },
  { code: "sk-SK", name: "Slovak", nativeName: "Slovenčina" },
  { code: "sl-SI", name: "Slovenian", nativeName: "Slovenščina" },
  { code: "so-SO", name: "Somali", nativeName: "Soomaali" },
  { code: "es-ES", name: "Spanish", nativeName: "Español" },
  { code: "es-MX", name: "Spanish (Mexico)", nativeName: "Español (MX)" },
  { code: "es-AR", name: "Spanish (Argentina)", nativeName: "Español (AR)" },
  { code: "sw-KE", name: "Swahili", nativeName: "Kiswahili" },
  { code: "sv-SE", name: "Swedish", nativeName: "Svenska" },
  { code: "tl-PH", name: "Tagalog", nativeName: "Tagalog" },
  { code: "tg-TJ", name: "Tajik", nativeName: "Тоҷикӣ" },
  { code: "ta-IN", name: "Tamil", nativeName: "தமிழ்" },
  { code: "te-IN", name: "Telugu", nativeName: "తెలుగు" },
  { code: "th-TH", name: "Thai", nativeName: "ไทย" },
  { code: "tr-TR", name: "Turkish", nativeName: "Türkçe" },
  { code: "tk-TM", name: "Turkmen", nativeName: "Türkmen" },
  { code: "uk-UA", name: "Ukrainian", nativeName: "Українська" },
  { code: "ur-PK", name: "Urdu", nativeName: "اردو" },
  { code: "ug-CN", name: "Uyghur", nativeName: "ئۇيغۇرچە" },
  { code: "uz-UZ", name: "Uzbek", nativeName: "O'zbek" },
  { code: "vi-VN", name: "Vietnamese", nativeName: "Tiếng Việt" },
  { code: "cy-GB", name: "Welsh", nativeName: "Cymraeg" },
  { code: "yi-US", name: "Yiddish", nativeName: "ייִדיש" },
  { code: "yo-NG", name: "Yoruba", nativeName: "Yorùbá" },
  { code: "zu-ZA", name: "Zulu", nativeName: "isiZulu" },
];

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

  // Dilleri alfabetik olarak sırala
  const sortedLanguages = [...WORLD_LANGUAGES].sort((a, b) =>
    a.name.localeCompare(b.name)
  );

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
          <Select
            value={voiceSettings?.language || "en-US"} // <-- DEĞİŞİKLİK BURADA
            onValueChange={handleLanguageChange}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select a language" />
            </SelectTrigger>
            <SelectContent className="max-h-60">
              {sortedLanguages.map((lang) => (
                <SelectItem key={lang.code} value={lang.code}>
                  <div className="flex items-center justify-between w-full">
                    <span>{lang.name}</span>
                    <span className="text-muted-foreground ml-2 text-xs">
                      {lang.nativeName}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
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
