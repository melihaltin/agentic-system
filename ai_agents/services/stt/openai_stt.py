"""
OpenAI Whisper STT Provider
"""

import tempfile
import openai

from core.interfaces import STTProvider


class OpenAISTT(STTProvider):
    """OpenAI Whisper STT Implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio using OpenAI Whisper"""
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()

            with open(temp_file.name, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
                return transcript.text
