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

            # Flatten the nested structure
            for template in templates:
                if template.get("sectors"):
                    template["sector_name"] = template["sectors"]["name"]
                    template["sector_slug"] = template["sectors"]["slug"]

                if template.get("agent_voices"):
                    template["default_voice_name"] = template["agent_voices"]["name"]
                else:
                    template["default_voice_name"] = None

                template.pop("sectors", None)
                template.pop("agent_voices", None)

            return templates

        except Exception as e:
            logger.error(f"Error fetching agent templates for sector {sector_id}: {e}")
            raise

    @staticmethod
    async def get_company_agents(company_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a company"""
        try:
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
            # Check if already exists (inactive)
            existing = (
                supabase.table("company_agents")
                .select("*")
                .eq("company_id", company_id)
                .eq("agent_template_id", agent_template_id)
                .execute()
            )

            config = config or {}

            if existing.data:
                # Reactivate existing agent
                update_data = {
                    "is_active": True,
                    "activated_at": "now()",
                    "is_configured": True,
                }

                # Update configuration if provided
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

                # Save integration configurations if provided
                if config.get("integrations"):
                    await IntegrationService.save_agent_integrations(
                        existing.data[0]["id"], config["integrations"]
                    )

                return result.data[0] if result.data else {}
            else:
                # Create new agent
                agent_data = {
                    "company_id": company_id,
                    "agent_template_id": agent_template_id,
                    "is_active": True,
                    "is_configured": True,
                    "activated_at": "now()",
                    "custom_name": config.get("custom_name"),
                    "custom_prompt": config.get("custom_prompt"),
                    "selected_voice_id": config.get("selected_voice_id"),
                    "configuration": config.get("configuration", {}),
                    "monthly_limit": config.get("monthly_limit"),
                    "daily_limit": config.get("daily_limit"),
                }

                result = supabase.table("company_agents").insert(agent_data).execute()

                # Save integration configurations if provided
                if config.get("integrations") and result.data:
                    await IntegrationService.save_agent_integrations(
                        result.data[0]["id"], config["integrations"]
                    )

                return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Error activating agent for company {company_id}: {e}")
            raise

    @staticmethod
    async def deactivate_agent_for_company(
        company_id: str, agent_id: str
    ) -> Dict[str, Any]:
        """Deactivate an agent for a company"""
        try:
            result = (
                supabase.table("company_agents")
                .update({"is_active": False})
                .eq("company_id", company_id)
                .eq("id", agent_id)
                .execute()
            )

            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(
                f"Error deactivating agent {agent_id} for company {company_id}: {e}"
            )
            raise

    @staticmethod
    async def toggle_agent_status(
        company_id: str, agent_id: str, is_active: bool
    ) -> Dict[str, Any]:
        """Toggle agent active status"""
        try:
            result = (
                supabase.table("company_agents")
                .update({"is_active": is_active})
                .eq("company_id", company_id)
                .eq("id", agent_id)
                .execute()
            )

            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Error toggling agent {agent_id}: {e}")
            raise

    @staticmethod
    async def update_company_agent(
        company_id: str, agent_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update company agent configuration"""
        try:
            # Only allow updates to specific fields
            allowed_fields = [
                "custom_name",
                "custom_prompt",
                "selected_voice_id",
                "configuration",
                "monthly_limit",
                "daily_limit",
                "is_active",
                "is_configured",
            ]

            update_data = {k: v for k, v in updates.items() if k in allowed_fields}

            print(
                f"🔄 Updating agent {agent_id} for company {company_id} with data: {update_data}"
            )
            if update_data:
                result = (
                    supabase.table("company_agents")
                    .update(update_data)
                    .eq("company_id", company_id)
                    .eq("id", agent_id)
                    .execute()
                )

                # Update integrations if provided
                if updates.get("integrations"):
                    await IntegrationService.save_agent_integrations(
                        agent_id, updates["integrations"]
                    )

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


class IntegrationService:
    """Service for managing integration configurations and API keys"""

    @staticmethod
    async def save_agent_integrations(agent_id: str, integrations: Dict[str, Any]):
        """Save integration configurations for an agent with encrypted API keys"""
        try:
            # Get company_id from agent
            agent_result = (
                supabase.table("company_agents")
                .select("company_id")
                .eq("id", agent_id)
                .execute()
            )

            if not agent_result.data:
                raise ValueError("Agent not found")

            company_id = agent_result.data[0]["company_id"]

            print(
                f"🔑 Saving integrations for agent {agent_id} of company {company_id}"
            )

            for provider_slug, config in integrations.items():
                if not config or not isinstance(config, dict):
                    continue

                # Get provider info
                provider_result = (
                    supabase.table("integration_providers")
                    .select("id, required_fields")
                    .eq("slug", provider_slug)
                    .execute()
                )

                if not provider_result.data:
                    continue

                provider_id = provider_result.data[0]["id"]

                # Create or update company integration configuration
                company_integration_result = (
                    supabase.table("company_integration_configurations")
                    .select("id")
                    .eq("company_id", company_id)
                    .eq("provider_id", provider_id)
                    .execute()
                )

                if company_integration_result.data:
                    # Update existing configuration
                    configuration_id = company_integration_result.data[0]["id"]
                else:
                    # Create new configuration
                    new_config = {
                        "company_id": company_id,
                        "provider_id": provider_id,
                        "configuration_name": f"{provider_slug}_config",
                        "is_active": True,
                        "is_default": True,
                    }

                    create_result = (
                        supabase.table("company_integration_configurations")
                        .insert(new_config)
                        .execute()
                    )

                    configuration_id = create_result.data[0]["id"]

                # Save encrypted credentials
                await IntegrationService._save_encrypted_credentials(
                    configuration_id, config
                )

                # Link agent to integration
                await IntegrationService._link_agent_to_integration(
                    agent_id, configuration_id
                )

        except Exception as e:
            logger.error(f"Error saving agent integrations: {e}")
            raise

    @staticmethod
    async def _save_encrypted_credentials(
        configuration_id: str, config: Dict[str, Any]
    ):
        """Save encrypted credentials for an integration configuration"""
        try:
            # Delete existing credentials
            supabase.table("integration_credentials").delete().eq(
                "configuration_id", configuration_id
            ).execute()

            # Save new credentials
            for key, value in config.items():
                if value and isinstance(value, str):
                    credential_data = {
                        "configuration_id": configuration_id,
                        "credential_key": key,
                        "encrypted_value": value,  # In production, this should be encrypted
                    }

                    supabase.table("integration_credentials").insert(
                        credential_data
                    ).execute()

        except Exception as e:
            logger.error(f"Error saving encrypted credentials: {e}")
            raise

    @staticmethod
    async def _link_agent_to_integration(agent_id: str, configuration_id: str):
        """Link agent to integration configuration"""
        try:
            # Check if link already exists
            existing_link = (
                supabase.table("agent_integration_links")
                .select("id")
                .eq("agent_id", agent_id)
                .eq("configuration_id", configuration_id)
                .execute()
            )

            if not existing_link.data:
                # Create new link
                link_data = {
                    "agent_id": agent_id,
                    "configuration_id": configuration_id,
                    "is_enabled": True,
                    "permissions": {},
                }

                supabase.table("agent_integration_links").insert(link_data).execute()
            else:
                # Update existing link to enabled
                supabase.table("agent_integration_links").update(
                    {"is_enabled": True}
                ).eq("id", existing_link.data[0]["id"]).execute()

        except Exception as e:
            logger.error(f"Error linking agent to integration: {e}")
            raise

    @staticmethod
    async def get_agent_integrations(agent_id: str) -> Dict[str, Any]:
        """Get integration configurations for an agent"""
        try:
            result = (
                supabase.table("agent_integration_links")
                .select(
                    """
                    *,
                    company_integration_configurations!inner(
                        *,
                        integration_providers!inner(name, slug, required_fields)
                    )
                """
                )
                .eq("agent_id", agent_id)
                .eq("is_enabled", True)
                .execute()
            )

            integrations = {}
            for link in result.data or []:
                config = link["company_integration_configurations"]
                provider = config["integration_providers"]

                # Get decrypted credentials (simplified for now)
                credentials_result = (
                    supabase.table("integration_credentials")
                    .select("credential_key, encrypted_value")
                    .eq("configuration_id", config["id"])
                    .execute()
                )

                credentials = {}
                for cred in credentials_result.data or []:
                    credentials[cred["credential_key"]] = cred["encrypted_value"]

                integrations[provider["slug"]] = credentials

            return integrations

        except Exception as e:
            logger.error(f"Error getting agent integrations: {e}")
            return {}


# Service instance
agent_service = AgentManagementService()
