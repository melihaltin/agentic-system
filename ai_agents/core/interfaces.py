"""
Abstract interfaces for voice services
"""

from abc import ABC, abstractmethod
from typing import Optional


class TTSProvider(ABC):
    """Text-to-Speech provider interface"""

    @abstractmethod
    def generate_speech(self, text: str, **kwargs) -> bytes:
        """Generate speech from text and return audio bytes"""
        pass

    @abstractmethod
    def generate_speech_url(self, text: str, **kwargs) -> str:
        """Generate speech and return accessible URL"""
        pass


class STTProvider(ABC):
    """Speech-to-Text provider interface"""

    @abstractmethod
    def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio bytes to text"""
        pass


class AudioStorage(ABC):
    """Audio storage interface for temporary files"""

    @abstractmethod
    def save_audio(self, audio_data: bytes, filename: Optional[str] = None) -> str:
        """Save audio and return accessible URL"""
        pass
