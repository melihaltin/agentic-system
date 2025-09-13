"""
Twilio STT Provider (fallback)
"""

from core.interfaces import STTProvider


class TwilioSTT(STTProvider):
    """Twilio built-in STT (default)"""

    def transcribe_audio(self, audio_data: bytes) -> str:
        # Twilio handles STT automatically in gather, this is for interface compliance
        raise NotImplementedError(
            "Twilio STT is handled automatically in VoiceResponse.gather()"
        )
