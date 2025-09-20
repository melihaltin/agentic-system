"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, Play, Check, User, Clock, Globe } from "lucide-react";
import { VoiceOption, VoicesResponse } from "@/types/admin.types";
import { voicesApi } from "@/lib/api/voices";

interface VoiceSelectorProps {
  selectedVoice?: VoiceOption;
  onVoiceSelect: (voice: VoiceOption) => void;
  className?: string;
}

const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  selectedVoice,
  onVoiceSelect,
  className = "",
}) => {
  const [voices, setVoices] = useState<VoiceOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playingVoiceId, setPlayingVoiceId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterGender, setFilterGender] = useState<string>("all");
  const [filterProvider, setFilterProvider] = useState<string>("all");

  // Çalan sesi kontrol etmek için tek Audio referansı
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    loadVoices();
    // bileşen unmount olunca sesi durdur
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const loadVoices = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response: VoicesResponse = await voicesApi.getVoices(true);
      setVoices(response.voices);
    } catch (err) {
      setError("Failed to load voices. Please try again.");
      console.error("Error loading voices:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlayPreview = (voice: VoiceOption) => {
    if (!voice.sample_url) return;

    // Önce varsa eski sesi durdur
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    // Yeni audio nesnesi oluştur
    const audio = new Audio(voice.sample_url);
    audioRef.current = audio;
    setPlayingVoiceId(voice.id);

    audio.play().catch((err) => console.error("Error playing preview:", err));

    // Bittiğinde state sıfırla
    audio.onended = () => {
      setPlayingVoiceId(null);
      audioRef.current = null;
    };
  };

  const filteredVoices = voices.filter((voice) => {
    const matchesSearch =
      voice.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (voice.accent &&
        voice.accent.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesGender =
      filterGender === "all" || voice.gender === filterGender;
    const matchesProvider =
      filterProvider === "all" || voice.provider === filterProvider;

    return matchesSearch && matchesGender && matchesProvider;
  });

  const providers = Array.from(new Set(voices.map((v) => v.provider)));

  if (isLoading) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-gray-600"></div>
          <span className="ml-3 text-sm text-gray-600">Loading voices...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <div className="border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-700">{error}</p>
          <button
            onClick={loadVoices}
            className="mt-3 text-sm text-gray-600 hover:text-gray-800 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className} space-y-6`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Select Voice</h3>
        <span className="text-sm text-gray-500">
          {filteredVoices.length} voices
        </span>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search voices..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
          />
        </div>

        <select
          value={filterGender}
          onChange={(e) => setFilterGender(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
        >
          <option value="all">All Genders</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="neutral">Neutral</option>
        </select>

        <select
          value={filterProvider}
          onChange={(e) => setFilterProvider(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
        >
          <option value="all">All Providers</option>
          {providers.map((provider) => (
            <option key={provider} value={provider}>
              {provider.charAt(0).toUpperCase() + provider.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Voice List */}
      <div className="max-h-80 overflow-y-auto">
        {filteredVoices.length === 0 ? (
          <div className="text-center py-8">
            <Search className="mx-auto h-8 w-8 text-gray-300 mb-3" />
            <p className="text-sm text-gray-500">No voices found</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredVoices.map((voice) => {
              const isSelected = selectedVoice?.id === voice.id;
              const isPlaying = playingVoiceId === voice.id;

              return (
                <div
                  key={voice.id}
                  className={`relative border rounded-lg p-4 cursor-pointer transition-colors ${
                    isSelected
                      ? "border-gray-900 bg-gray-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => onVoiceSelect(voice)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-medium text-gray-900">
                          {voice.name}
                        </h4>
                        {isSelected && (
                          <Check className="h-4 w-4 text-gray-900" />
                        )}
                      </div>

                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        {voice.gender && (
                          <div className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {voice.gender.charAt(0).toUpperCase() +
                              voice.gender.slice(1)}
                          </div>
                        )}
                        {voice.age_group && (
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {voice.age_group.charAt(0).toUpperCase() +
                              voice.age_group.slice(1)}
                          </div>
                        )}
                        {voice.accent && (
                          <div className="flex items-center gap-1">
                            <Globe className="h-3 w-3" />
                            {voice.accent}
                          </div>
                        )}
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {voice.provider.charAt(0).toUpperCase() +
                            voice.provider.slice(1)}
                        </span>
                      </div>
                    </div>

                    {voice.sample_url && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handlePlayPreview(voice);
                        }}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        disabled={isPlaying}
                      >
                        <Play
                          className={`h-4 w-4 ${
                            isPlaying ? "text-gray-900" : "text-gray-600"
                          }`}
                        />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Voice */}
      {selectedVoice && (
        <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-gray-900 rounded-full"></div>
              <span className="text-sm text-gray-900 font-medium">
                {selectedVoice.name}
              </span>
            </div>
            {selectedVoice.sample_url && (
              <button
                onClick={() => handlePlayPreview(selectedVoice)}
                className="text-sm text-gray-600 hover:text-gray-900 px-2 py-1 hover:bg-gray-100 rounded transition-colors"
                disabled={playingVoiceId === selectedVoice.id}
              >
                {playingVoiceId === selectedVoice.id ? "Playing..." : "Preview"}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Voice Settings Component
export default VoiceSelector;
