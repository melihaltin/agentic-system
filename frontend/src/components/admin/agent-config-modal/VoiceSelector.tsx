"use client";

import React, { useState, useEffect } from "react";
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

  useEffect(() => {
    loadVoices();
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

  const handlePlayPreview = async (voice: VoiceOption) => {
    if (!voice.sample_url) {
      return;
    }

    try {
      setPlayingVoiceId(voice.id);
      await voicesApi.playVoicePreview(voice);
    } catch (err) {
      console.error("Error playing preview:", err);
    } finally {
      setPlayingVoiceId(null);
    }
  };

  // Filter voices based on search and filters
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

  // Get unique providers
  const providers = Array.from(new Set(voices.map((v) => v.provider)));

  if (isLoading) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading voices...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg
              className="h-5 w-5 text-red-400 mr-2"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-red-800">{error}</span>
          </div>
          <button
            onClick={loadVoices}
            className="mt-2 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-800 rounded text-sm transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Header and Filters */}
      <div className="mb-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Select Voice</h3>
          <span className="text-sm text-gray-500">
            {filteredVoices.length} voices available
          </span>
        </div>

        {/* Search and Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg
                className="h-4 w-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search voices..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>

          {/* Gender Filter */}
          <select
            value={filterGender}
            onChange={(e) => setFilterGender(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="all">All Genders</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="neutral">Neutral</option>
          </select>

          {/* Provider Filter */}
          <select
            value={filterProvider}
            onChange={(e) => setFilterProvider(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="all">All Providers</option>
            {providers.map((provider) => (
              <option key={provider} value={provider}>
                {provider.charAt(0).toUpperCase() + provider.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Voice Cards Grid */}
      <div className="max-h-96 overflow-y-auto">
        {filteredVoices.length === 0 ? (
          <div className="text-center py-8">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No voices found
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search or filters.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {filteredVoices.map((voice) => {
              const isSelected = selectedVoice?.id === voice.id;
              const isPlaying = playingVoiceId === voice.id;

              return (
                <div
                  key={voice.id}
                  className={`relative border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                    isSelected
                      ? "border-blue-500 bg-blue-50 shadow-md"
                      : "border-gray-200 bg-white hover:border-gray-300"
                  }`}
                  onClick={() => onVoiceSelect(voice)}
                >
                  {/* Selection indicator */}
                  {isSelected && (
                    <div className="absolute top-2 right-2">
                      <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                        <svg
                          className="w-3 h-3 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      </div>
                    </div>
                  )}

                  {/* Premium badge */}
                  {voice.is_premium && (
                    <div className="absolute top-2 left-2">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                        <svg
                          className="w-3 h-3 mr-1"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        Premium
                      </span>
                    </div>
                  )}

                  <div className="mt-6">
                    {/* Voice Info */}
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 text-sm">
                        {voice.name}
                      </h4>

                      {/* Play Button */}
                      {voice.sample_url && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePlayPreview(voice);
                          }}
                          className={`p-1.5 rounded-full transition-all ${
                            isPlaying
                              ? "bg-blue-500 text-white"
                              : "bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-800"
                          }`}
                          disabled={isPlaying}
                        >
                          {isPlaying ? (
                            <div className="animate-pulse">
                              <svg
                                className="w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                                />
                              </svg>
                            </div>
                          ) : (
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8m-7 0a4 4 0 118 0H7z"
                              />
                            </svg>
                          )}
                        </button>
                      )}
                    </div>

                    {/* Voice Details */}
                    <div className="space-y-1">
                      <div className="flex items-center text-xs text-gray-600">
                        <span className="flex items-center">
                          <svg
                            className="w-3 h-3 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                            />
                          </svg>
                          {voice.gender
                            ? voice.gender.charAt(0).toUpperCase() +
                              voice.gender.slice(1)
                            : "Unknown"}
                        </span>
                        {voice.age_group && (
                          <span className="ml-3 flex items-center">
                            <svg
                              className="w-3 h-3 mr-1"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                            {voice.age_group.charAt(0).toUpperCase() +
                              voice.age_group.slice(1)}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                          {voice.provider.charAt(0).toUpperCase() +
                            voice.provider.slice(1)}
                        </span>
                        {voice.accent && (
                          <span className="text-xs text-gray-500">
                            {voice.accent}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Voice Summary */}
      {selectedVoice && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-blue-900">
                Selected:{" "}
              </span>
              <span className="text-sm text-blue-800">
                {selectedVoice.name}
              </span>
              {selectedVoice.is_premium && (
                <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded">
                  Premium
                </span>
              )}
            </div>
            {selectedVoice.sample_url && (
              <button
                onClick={() => handlePlayPreview(selectedVoice)}
                className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 px-2 py-1 rounded transition-colors"
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

export default VoiceSelector;
