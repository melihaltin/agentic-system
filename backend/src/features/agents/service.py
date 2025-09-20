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


class AgentManagementService:
    """Service for agent management operations"""

    @staticmethod
    async def get_sectors(is_active: Optional[bool] = True) -> List[Dict[str, Any]]:
        """Get all sectors"""
        try:
            query = supabase.table("sectors").select("*")
            if is_active is not None:
                query = query.eq("is_active", is_active)

            result = query.order("name").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching sectors: {e}")
            raise

    @staticmethod
    async def get_agent_templates_by_sector(sector_id: str) -> List[Dict[str, Any]]:
        """Get agent templates for a specific sector"""
        try:
            # Get basic templates for sector
            templates_result = (
                supabase.table("agent_templates")
                .select(
                    """
                *,
                sectors!inner(name, slug),
                agent_voices(name)
            """
                )
                .eq("sector_id", sector_id)
                .eq("is_active", True)
                .order("is_featured", desc=True)
                .order("sort_order")
                .order("name")
                .execute()
            )

            templates = templates_result.data if templates_result.data else []

            # Flatten the nested structure and get integrations for each template
            for template in templates:
                # Flatten sector info
                if template.get("sectors"):
                    template["sector_name"] = template["sectors"]["name"]
                    template["sector_slug"] = template["sectors"]["slug"]

                # Flatten voice info
                if template.get("agent_voices"):
                    template["default_voice_name"] = template["agent_voices"]["name"]
                else:
                    template["default_voice_name"] = None

                # Clean up nested objects
                template.pop("sectors", None)
                template.pop("agent_voices", None)

                # Get required integrations (if table exists)
                try:
                    integrations_result = (
                        supabase.table("integration_providers")
                        .select("*")
                        .eq("is_active", True)
                        .execute()
                    )
                    template["required_integrations"] = integrations_result.data or []
                except Exception:
                    template["required_integrations"] = []

            return templates

        except Exception as e:
            logger.error(f"Error fetching agent templates for sector {sector_id}: {e}")
            raise

    @staticmethod
    async def get_company_agents(company_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a company"""
        try:
            # Get company agents with related data using joins
            result = (
                supabase.table("company_agents")
                .select(
                    """
                *,
                agent_templates!inner(
                    name,
                    slug,
                    description,
                    agent_type,
                    icon,
                    capabilities,
                    requires_voice,
                    sectors!inner(name, slug)
                ),
                agent_voices(name, provider)
            """
                )
                .eq("company_id", company_id)
                .order("is_active", desc=True)
                .order("created_at", desc=True)
                .execute()
            )

            agents = result.data if result.data else []

            # Flatten nested structure
            for agent in agents:
                if agent.get("agent_templates"):
                    template = agent["agent_templates"]
                    agent["template_name"] = template["name"]
                    agent["template_slug"] = template["slug"]
                    agent["template_description"] = template["description"]
                    agent["agent_type"] = template["agent_type"]
                    agent["icon"] = template["icon"]
                    agent["capabilities"] = template["capabilities"]
                    agent["requires_voice"] = template["requires_voice"]

                    if template.get("sectors"):
                        agent["sector_name"] = template["sectors"]["name"]
                        agent["sector_slug"] = template["sectors"]["slug"]

                if agent.get("agent_voices"):
                    agent["voice_name"] = agent["agent_voices"]["name"]
                    agent["voice_provider"] = agent["agent_voices"]["provider"]
                else:
                    agent["voice_name"] = None
                    agent["voice_provider"] = None

                # Clean up nested objects
                agent.pop("agent_templates", None)
                agent.pop("agent_voices", None)

            return agents

        except Exception as e:
            logger.error(f"Error fetching company agents for {company_id}: {e}")
            raise

    @staticmethod
    async def activate_agent_for_company(
        company_id: str, agent_template_id: str, config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Activate an agent template for a company"""
        try:
            # Check if already activated
            existing = (
                supabase.table("company_agents")
                .select("*")
                .eq("company_id", company_id)
                .eq("agent_template_id", agent_template_id)
                .execute()
            )

            if existing.data:
                # Update existing
                update_data = {"is_active": True, "activated_at": "now()"}
                if config:
                    if config.get("custom_name"):
                        update_data["custom_name"] = config["custom_name"]
                    if config.get("custom_prompt"):
                        update_data["custom_prompt"] = config["custom_prompt"]
                    if config.get("selected_voice_id"):
                        update_data["selected_voice_id"] = config["selected_voice_id"]
                    if config.get("configuration"):
                        update_data["configuration"] = config["configuration"]

                result = (
                    supabase.table("company_agents")
                    .update(update_data)
                    .eq("id", existing.data[0]["id"])
                    .execute()
                )
                return result.data[0] if result.data else {}
            else:
                # Create new
                agent_data = {
                    "company_id": company_id,
                    "agent_template_id": agent_template_id,
                    "is_active": True,
                    "activated_at": "now()",
                    "configuration": config.get("configuration", {}) if config else {},
                }

                if config:
                    if config.get("custom_name"):
                        agent_data["custom_name"] = config["custom_name"]
                    if config.get("custom_prompt"):
                        agent_data["custom_prompt"] = config["custom_prompt"]
                    if config.get("selected_voice_id"):
                        agent_data["selected_voice_id"] = config["selected_voice_id"]
                    if config.get("monthly_limit"):
                        agent_data["monthly_limit"] = config["monthly_limit"]
                    if config.get("daily_limit"):
                        agent_data["daily_limit"] = config["daily_limit"]

                result = supabase.table("company_agents").insert(agent_data).execute()
                return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Error activating agent for company {company_id}: {e}")
            raise

    @staticmethod
    async def deactivate_agent_for_company(company_id: str, agent_id: str) -> Dict[str, Any]:
        """Deactivate an agent for a company"""
        try:
            logger.info(f"Deactivating agent {agent_id} for company {company_id}")
            result = (
                supabase.table("company_agents")
                .update({"is_active": False})
                .eq("company_id", company_id)
                .eq("id", agent_id)
                .execute()
            )
            
            logger.info(f"Deactivate query result: {result.data}")
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(
                f"Error deactivating agent {agent_id} for company {company_id}: {e}"
            )
            raise

    @staticmethod
    async def update_company_agent(
        company_id: str, agent_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update company agent configuration"""
        try:
            logger.info(f"Updating agent {agent_id} for company {company_id} with updates: {updates}")
            # Only allow updates to specific fields
            allowed_fields = [
                "custom_name",
                "custom_prompt",
                "selected_voice_id",
                "configuration",
                "monthly_limit",
                "daily_limit",
                "is_active",
            ]

            update_data = {k: v for k, v in updates.items() if k in allowed_fields}
            logger.info(f"Filtered update data: {update_data}")

            if update_data:
                result = (
                    supabase.table("company_agents")
                    .update(update_data)
                    .eq("company_id", company_id)
                    .eq("id", agent_id)
                    .execute()
                )
                logger.info(f"Update query result: {result.data}")
                return result.data[0] if result.data else {}

            return {}

        except Exception as e:
            logger.error(f"Error updating company agent {agent_id}: {e}")
            raise

    @staticmethod
    async def get_integration_providers(
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get integration providers"""
        try:
            query = (
                supabase.table("integration_providers")
                .select("*")
                .eq("is_active", True)
            )

            if category:
                query = query.eq("category", category)

            result = query.order("name").execute()
            return result.data

        except Exception as e:
            logger.error(f"Error fetching integration providers: {e}")
            raise


# Service instance
agent_service = AgentManagementService()
