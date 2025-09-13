"""
Twilio TTS Provider (fallback)
"""

from core.interfaces import TTSProvider


class TwilioTTS(TTSProvider):
    """Default Twilio TTS (fallback)"""

    def generate_speech(self, text: str, **kwargs) -> bytes:
        # Twilio doesn't return audio bytes directly, this is for interface compliance
        raise NotImplementedError("Twilio TTS works through VoiceResponse.say()")

    def generate_speech_url(self, text: str, **kwargs) -> str:
        # Return text for Twilio's built-in TTS
        return text
