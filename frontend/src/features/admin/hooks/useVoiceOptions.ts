import { useState, useEffect } from 'react';
import { VoiceOption } from '@/types/admin.types';
import { AgentService } from '../services/agent-service';

export const useVoiceOptions = () => {
  const [voiceOptions, setVoiceOptions] = useState<VoiceOption[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadVoiceOptions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const voices = await AgentService.loadVoiceOptions();
      setVoiceOptions(voices);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load voice options');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadVoiceOptions();
  }, []);

  const playVoicePreview = (previewUrl: string) => {
    // In a real implementation, this would play the audio preview
    console.log('Playing voice preview:', previewUrl);
    // const audio = new Audio(previewUrl);
    // audio.play();
  };

  return {
    voiceOptions,
    isLoading,
    error,
    playVoicePreview,
    refetch: loadVoiceOptions,
  };
};
