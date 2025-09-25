import httpx
import logging
from typing import List, Dict, Any, Optional
from src.core.config import settings
from src.core.database import supabase
from src.features.agents.models import (
    ElevenLabsVoice,
    AgentVoiceResponse,
    SyncVoicesResponse,
)

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for ElevenLabs API integration"""

    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        print(
            f"🔑 Initializing ElevenLabsService with provided API key: {self.api_key}"
        )
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}

    async def fetch_voices_from_elevenlabs(self) -> List[ElevenLabsVoice]:
        """Fetch all voices from ElevenLabs API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/voices", headers=self.headers, timeout=30.0
                )
                response.raise_for_status()

                data = response.json()
                voices = []

                for voice_data in data.get("voices", []):
                    voice = ElevenLabsVoice(
                        voice_id=voice_data.get("voice_id"),
                        name=voice_data.get("name"),
                        category=voice_data.get("category"),
                        labels=voice_data.get("labels", {}),
                        description=voice_data.get("description"),
                        preview_url=voice_data.get("preview_url"),
                        available_for_tiers=voice_data.get("available_for_tiers", []),
                        settings=voice_data.get("settings"),
                    )
                    voices.append(voice)

                return voices

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching voices from ElevenLabs: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching voices from ElevenLabs: {e}")
            raise

    def _extract_voice_metadata(self, voice: ElevenLabsVoice) -> Dict[str, Any]:
        """Extract metadata from ElevenLabs voice data"""
        labels = voice.labels or {}

        # Extract gender from labels
        gender = None
        if "gender" in labels:
            gender = labels["gender"]
        elif "male" in labels:
            gender = "male" if labels["male"] else "female"

        # Extract age group from labels
        age_group = None
        age_descriptors = labels.get("descriptive", [])
        if isinstance(age_descriptors, list):
            for desc in age_descriptors:
                if "young" in desc.lower():
                    age_group = "young"
                    break
                elif "old" in desc.lower() or "elderly" in desc.lower():
                    age_group = "old"
                    break
                elif "middle" in desc.lower():
                    age_group = "middle"
                    break

        # Extract accent from labels
        accent = labels.get("accent")

        # Determine if premium
        is_premium = "professional" in (voice.available_for_tiers or [])

        return {
            "gender": gender,
            "age_group": age_group,
            "accent": accent,
            "is_premium": is_premium,
            "elevenlabs_labels": labels,
            "elevenlabs_settings": voice.settings,
            "elevenlabs_category": voice.category,
        }

    async def save_voice_to_database(self, voice: ElevenLabsVoice) -> bool:
        """Save a voice to the database"""
        try:
            metadata = self._extract_voice_metadata(voice)

            voice_data = {
                "name": voice.name,
                "provider": "elevenlabs",
                "voice_id": voice.voice_id,
                "language": "tr-TR",  # Default to Turkish, can be updated later
                "gender": metadata.get("gender"),
                "age_group": metadata.get("age_group"),
                "accent": metadata.get("accent"),
                "sample_url": voice.preview_url,
                "is_premium": metadata.get("is_premium", False),
                "is_active": True,
                "metadata": {
                    "elevenlabs_labels": metadata.get("elevenlabs_labels"),
                    "elevenlabs_settings": metadata.get("elevenlabs_settings"),
                    "elevenlabs_category": metadata.get("elevenlabs_category"),
                    "description": voice.description,
                },
            }

            # Check if voice already exists
            existing = (
                supabase.table("agent_voices")
                .select("id")
                .eq("voice_id", voice.voice_id)
                .eq("provider", "elevenlabs")
                .execute()
            )

            if existing.data:
                # Update existing voice
                supabase.table("agent_voices").update(voice_data).eq(
                    "voice_id", voice.voice_id
                ).eq("provider", "elevenlabs").execute()
            else:
                # Insert new voice
                supabase.table("agent_voices").insert(voice_data).execute()

            return True

        except Exception as e:
            logger.error(f"Error saving voice {voice.voice_id} to database: {e}")
            return False

    async def sync_voices_from_elevenlabs(self) -> SyncVoicesResponse:
        """Sync all voices from ElevenLabs to database"""
        try:
            # Fetch voices from ElevenLabs
            voices = await self.fetch_voices_from_elevenlabs()

            synced_count = 0
            skipped_count = 0
            errors = []

            for voice in voices:
                try:
                    success = await self.save_voice_to_database(voice)
                    if success:
                        synced_count += 1
                    else:
                        skipped_count += 1
                        errors.append(f"Failed to save voice: {voice.name}")
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"Error processing voice {voice.name}: {str(e)}")

            return SyncVoicesResponse(
                success=True,
                message=f"Successfully synced {synced_count} voices, skipped {skipped_count}",
                synced_count=synced_count,
                skipped_count=skipped_count,
                errors=errors,
            )

        except Exception as e:
            logger.error(f"Error syncing voices: {e}")
            return SyncVoicesResponse(
                success=False,
                message=f"Sync failed: {str(e)}",
                synced_count=0,
                skipped_count=0,
                errors=[str(e)],
            )

    async def get_voices_from_database(
        self, is_active: Optional[bool] = True
    ) -> List[AgentVoiceResponse]:
        """Get voices from database"""
        try:
            query = supabase.table("agent_voices").select("*")

            if is_active is not None:
                query = query.eq("is_active", is_active)

            result = query.order("name").execute()

            voices = []
            for voice_data in result.data:
                voice = AgentVoiceResponse(
                    id=voice_data["id"],
                    name=voice_data["name"],
                    provider=voice_data["provider"],
                    voice_id=voice_data["voice_id"],
                    language=voice_data["language"],
                    gender=voice_data.get("gender"),
                    age_group=voice_data.get("age_group"),
                    accent=voice_data.get("accent"),
                    sample_url=voice_data.get("sample_url"),
                    is_premium=voice_data.get("is_premium", False),
                    is_active=voice_data.get("is_active", True),
                    metadata=voice_data.get("metadata"),
                    created_at=voice_data["created_at"],
                    updated_at=voice_data["updated_at"],
                )
                voices.append(voice)

            return voices

        except Exception as e:
            logger.error(f"Error fetching voices from database: {e}")
            raise


# Service instance
elevenlabs_service = ElevenLabsService()


if __name__ == "__main__":
    import asyncio

    async def main():
        """
        ElevenLabs'ten tüm sesleri çek ve Supabase'e kaydet.
        """
        result = await elevenlabs_service.sync_voices_from_elevenlabs()
        print(
            f"✅ Sync tamamlandı:\n"
            f"  - Senkronize edilen: {result.synced_count}\n"
            f"  - Atlanan: {result.skipped_count}\n"
            f"  - Mesaj: {result.message}\n"
        )

        # Hata varsa detaylarını da göster
        if result.errors:
            print("⚠️  Hatalar:")
            for err in result.errors:
                print(f"   • {err}")

    asyncio.run(main())
