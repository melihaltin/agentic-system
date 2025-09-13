"""
ElevenLabs TTS Provider
"""

import requests
import base64

from core.interfaces import TTSProvider


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs TTS Implementation"""

    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = "https://api.elevenlabs.io/v1"

    def generate_speech(self, text: str, **kwargs) -> bytes:
        """Generate speech with ElevenLabs API"""
        voice_id = kwargs.get("voice_id", self.voice_id)
        model_id = kwargs.get("model_id", "eleven_monolingual_v1")

        url = f"{self.base_url}/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }

        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": kwargs.get("stability", 0.5),
                "similarity_boost": kwargs.get("similarity_boost", 0.5),
            },
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(
                f"ElevenLabs API error: {response.status_code} - {response.text}"
            )

    def generate_speech_url(self, text: str, **kwargs) -> str:
        """Generate speech and save to accessible URL"""
        audio_data = self.generate_speech(text, **kwargs)
        storage = kwargs.get("storage")
        if storage:
            return storage.save_audio(audio_data)
        else:
            # Fallback to base64 for small audio
            audio_b64 = base64.b64encode(audio_data).decode()
            return f"data:audio/mpeg;base64,{audio_b64}"
