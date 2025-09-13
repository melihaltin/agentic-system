"""
Main voice processing service
"""

from typing import Optional

from core.interfaces import TTSProvider, STTProvider, AudioStorage


class VoiceService:
    """Main voice processing service"""

    def __init__(
        self,
        tts_provider: TTSProvider,
        stt_provider: Optional[STTProvider] = None,
        audio_storage: Optional[AudioStorage] = None,
    ):
        self.tts_provider = tts_provider
        self.stt_provider = stt_provider
        self.audio_storage = audio_storage

    def text_to_speech(self, text: str, use_url: bool = True, **kwargs) -> str:
        """Convert text to speech"""
        kwargs["storage"] = self.audio_storage

        if use_url and hasattr(self.tts_provider, "generate_speech_url"):
            return self.tts_provider.generate_speech_url(text, **kwargs)
        else:
            # For Twilio's built-in TTS
            return text

    def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text"""
        if self.stt_provider:
            return self.stt_provider.transcribe_audio(audio_data)
        else:
            raise NotImplementedError("No STT provider configured")
