import httpx
import logging
from typing import List, Dict, Any, Optional
from src.core.database import supabase
from src.features.agents.services.integration_service import IntegrationService

logger = logging.getLogger(__name__)


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

                # Extract integrations from configuration or integrations field
                integrations_to_save = None
                if config.get("integrationConfigs"):
                    integrations_to_save = config["integrationConfigs"]
                elif config.get("integrations"):
                    integrations_to_save = config["integrations"]
                elif config.get("configuration") and isinstance(
                    config["configuration"], dict
                ):
                    # Check if configuration contains integration data
                    conf = config["configuration"]
                    if any(
                        key in conf
                        for key in [
                            "shopify",
                            "woocommerce",
                            "magento",
                            "ticimax",
                            "custom_booking",
                        ]
                    ):
                        integrations_to_save = conf

                # Update configuration if provided
                if config.get("custom_name"):
                    update_data["custom_name"] = config["custom_name"]
                if config.get("custom_prompt"):
                    update_data["custom_prompt"] = config["custom_prompt"]
                if config.get("selected_voice_id"):
                    update_data["selected_voice_id"] = config["selected_voice_id"]
                if config.get("language"):
                    # Persist selected language directly on company_agents
                    update_data["language"] = config["language"]

                # Store only integration references in configuration field (no sensitive data)
                if integrations_to_save:
                    integration_summary = {}
                    for provider_slug, provider_config in integrations_to_save.items():
                        integration_summary[provider_slug] = {
                            "enabled": True,
                            "provider_slug": provider_slug,
                            "configured_fields_count": (
                                len(provider_config.keys()) if provider_config else 0
                            ),
                            "last_updated": "now()",
                            # Reference to find the actual credentials in integration_credentials table
                            "configuration_reference": f"agent_{existing.data[0]['id']}_provider_{provider_slug}",
                        }
                    update_data["configuration"] = {"integrations": integration_summary}
                else:
                    update_data["configuration"] = {}

                result = (
                    supabase.table("company_agents")
                    .update(update_data)
                    .eq("id", existing.data[0]["id"])
                    .execute()
                )

                # Save integration configurations to proper tables
                if integrations_to_save:
                    print(
                        f"🔗 Saving integrations during activation: {integrations_to_save}"
                    )
                    await IntegrationService.save_agent_integrations(
                        existing.data[0]["id"], integrations_to_save
                    )

                return result.data[0] if result.data else {}
            else:
                # Create new agent
                # Extract integrations from configuration or integrations field
                integrations_to_save = None
                if config.get("integrationConfigs"):
                    integrations_to_save = config["integrationConfigs"]
                elif config.get("integrations"):
                    integrations_to_save = config["integrations"]
                elif config.get("configuration") and isinstance(
                    config["configuration"], dict
                ):
                    # Check if configuration contains integration data
                    conf = config["configuration"]
                    if any(
                        key in conf
                        for key in [
                            "shopify",
                            "woocommerce",
                            "magento",
                            "ticimax",
                            "custom_booking",
                        ]
                    ):
                        integrations_to_save = conf

                # Prepare configuration with integration references only (no sensitive data)
                configuration_data = {}
                if integrations_to_save:
                    integration_summary = {}
                    for provider_slug, provider_config in integrations_to_save.items():
                        integration_summary[provider_slug] = {
                            "enabled": True,
                            "provider_slug": provider_slug,
                            "configured_fields_count": (
                                len(provider_config.keys()) if provider_config else 0
                            ),
                            "last_updated": "now()",
                            # Reference to find the actual credentials - will be updated after insert
                            "configuration_reference": f"pending_agent_creation",
                        }
                    configuration_data = {"integrations": integration_summary}

                agent_data = {
                    "company_id": company_id,
                    "agent_template_id": agent_template_id,
                    "is_active": True,
                    "is_configured": True,
                    "activated_at": "now()",
                    "custom_name": config.get("custom_name"),
                    "custom_prompt": config.get("custom_prompt"),
                    "selected_voice_id": config.get("selected_voice_id"),
                    "language": config.get("language") or "en-US",
                    "configuration": configuration_data,
                    "monthly_limit": config.get("monthly_limit"),
                    "daily_limit": config.get("daily_limit"),
                }

                result = supabase.table("company_agents").insert(agent_data).execute()

                # Save integration configurations to proper tables
                if integrations_to_save and result.data:
                    agent_id = result.data[0]["id"]
                    print(
                        f"🔗 Saving integrations during new agent creation: {integrations_to_save}"
                    )
                    await IntegrationService.save_agent_integrations(
                        agent_id, integrations_to_save
                    )

                    # Update configuration with correct references after agent creation
                    if configuration_data.get("integrations"):
                        updated_integration_summary = {}
                        for provider_slug, summary in configuration_data[
                            "integrations"
                        ].items():
                            summary["configuration_reference"] = (
                                f"agent_{agent_id}_provider_{provider_slug}"
                            )
                            updated_integration_summary[provider_slug] = summary

                        # Update the agent with correct references
                        supabase.table("company_agents").update(
                            {
                                "configuration": {
                                    "integrations": updated_integration_summary
                                }
                            }
                        ).eq("id", agent_id).execute()

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
                "language",
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

            # Extract integrations from configuration if they exist
            integrations_to_save = None
            if update_data.get("configuration"):
                # Check if configuration contains integration data
                config = update_data["configuration"]
                if isinstance(config, dict) and any(
                    key in config
                    for key in [
                        "shopify",
                        "woocommerce",
                        "magento",
                        "ticimax",
                        "custom_booking",
                    ]
                ):
                    integrations_to_save = config

            # Also check for direct integrations field
            if updates.get("integrations"):
                integrations_to_save = updates["integrations"]

            # Update configuration with integration references only (no sensitive data)
            if integrations_to_save:
                integration_summary = {}
                for provider_slug, provider_config in integrations_to_save.items():
                    integration_summary[provider_slug] = {
                        "enabled": True,
                        "provider_slug": provider_slug,
                        "configured_fields_count": (
                            len(provider_config.keys()) if provider_config else 0
                        ),
                        "last_updated": "now()",
                        # Reference to find the actual credentials in integration_credentials table
                        "configuration_reference": f"agent_{agent_id}_provider_{provider_slug}",
                    }
                update_data["configuration"] = {"integrations": integration_summary}

            if update_data:
                result = (
                    supabase.table("company_agents")
                    .update(update_data)
                    .eq("company_id", company_id)
                    .eq("id", agent_id)
                    .execute()
                )

                # Save integrations to proper tables
                if integrations_to_save:
                    print(
                        f"🔗 Saving integrations to proper tables: {integrations_to_save}"
                    )
                    await IntegrationService.save_agent_integrations(
                        agent_id, integrations_to_save
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


agent_service = AgentManagementService()
