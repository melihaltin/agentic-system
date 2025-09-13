"""
Audio storage service for temporary audio files
"""

import os
import time
from typing import Optional

from core.interfaces import AudioStorage


class LocalAudioStorage(AudioStorage):
    """Local file storage for development"""

    def __init__(self, base_url: str, storage_path: str = "/tmp/audio"):
        self.base_url = base_url.rstrip("/")
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def save_audio(self, audio_data: bytes, filename: Optional[str] = None) -> str:
        if not filename:
            filename = f"audio_{int(time.time() * 1000)}.mp3"

        file_path = os.path.join(self.storage_path, filename)

        with open(file_path, "wb") as f:
            f.write(audio_data)

        return f"{self.base_url}/audio/{filename}"
