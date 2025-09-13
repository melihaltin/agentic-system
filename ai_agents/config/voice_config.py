"""
Voice service configuration module
"""

import os

from services.voice_service import VoiceService
from services.tts.elevenlabs import ElevenLabsTTS
from services.tts.twilio import TwilioTTS
from services.stt.openai_stt import OpenAISTT
from services.stt.twilio import TwilioSTT
from services.audio_storage import LocalAudioStorage


class VoiceConfig:
    """Voice service configuration"""

    @staticmethod
    def create_elevenlabs_config() -> VoiceService:
        """Create ElevenLabs configuration"""
        tts = ElevenLabsTTS(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        )

        audio_storage = LocalAudioStorage(
            base_url=os.getenv("WEBHOOK_BASE_URL"),
            storage_path=os.getenv("AUDIO_STORAGE_PATH", "/tmp/audio"),
        )

        stt = None
        if os.getenv("OPENAI_API_KEY"):
            stt = OpenAISTT(os.getenv("OPENAI_API_KEY"))

        return VoiceService(
            tts_provider=tts, stt_provider=stt, audio_storage=audio_storage
        )

    @staticmethod
    def create_twilio_config() -> VoiceService:
        """Create default Twilio configuration"""
        tts = TwilioTTS()
        stt = TwilioSTT()
        return VoiceService(tts_provider=tts, stt_provider=stt)
