"""
Agent Integration Service
Service for fetching agent and integration data from the database
"""

from typing import List, Dict, Any, Optional
from src.core.database import supabase
from src.core.config import settings
import json


class AgentIntegrationService:
    """Service for managing agent integrations"""

    def __init__(self):
        self.client = supabase

    async def fetch_agents_with_integrations(self) -> List[Dict[str, Any]]:
        """
        Fetch all active company agents with their integration configurations
        Returns a list of agents with their integration data
        """
        try:
            # Query to get agents with their integrations
            response = (
                self.client.table("company_agents")
                .select(
                    """
                *,
                company_profile(
                    id,
                    company_name,
                    business_category,
                    phone_number,
                    website,
                    timezone
                ),
                agent_templates(
                    id,
                    name,
                    slug,
                    agent_type,
                    capabilities
                ),
                agent_voices(
                    id,
                    name,
                    provider,
                    voice_id,
                    language
                ),
                agent_integration_links(
                    id,
                    is_enabled,
                    permissions,
                    company_integration_configurations(
                        id,
                        configuration_name,
                        is_active,
                        is_default,
                        webhook_url,
                        sync_status,
                        last_sync_at,
                        integration_providers(
                            id,
                            name,
                            slug,
                            provider_type,
                            auth_type,
                            webhook_support
                        )
                    )
                )
                """
                )
                .eq("is_active", True)
                .execute()
            )

            if not response.data:
                print("❌ No active agents found")
                return []

            # Process and format the data
            formatted_agents = []
            for agent_data in response.data:
                formatted_agent = self._format_agent_data(agent_data)
                formatted_agents.append(formatted_agent)

            print(
                f"✅ Successfully fetched {len(formatted_agents)} active agents with integrations"
            )
            return formatted_agents

        except Exception as e:
            print(f"❌ Error fetching agents with integrations: {str(e)}")
            return []

    def _format_agent_data(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw agent data into structured response
        """
        # Extract integrations data
        integrations = {}

        if agent_data.get("agent_integration_links"):
            for link in agent_data["agent_integration_links"]:
                config = link.get("company_integration_configurations", {})
                provider = config.get("integration_providers", {})

                if provider and config.get("is_active", False):
                    provider_slug = provider.get("slug", "unknown")
                    integrations[provider_slug] = {
                        "enabled": link.get("is_enabled", False),
                        "configuration_reference": f"agent_{agent_data['id']}_provider_{provider_slug}",
                        "provider_name": provider.get("name"),
                        "provider_type": provider.get("provider_type"),
                        "auth_type": provider.get("auth_type"),
                        "webhook_support": provider.get("webhook_support", False),
                        "webhook_url": config.get("webhook_url"),
                        "sync_status": config.get("sync_status"),
                        "last_sync_at": config.get("last_sync_at"),
                        "configuration_name": config.get("configuration_name"),
                        "permissions": link.get("permissions", {}),
                    }

        # Format the complete agent data
        # Build formatted data safely
        formatted_data = {
            "agent_id": agent_data["id"],
            "agent_info": {
                "custom_name": agent_data.get("custom_name"),
                "is_configured": agent_data.get("is_configured", False),
                "total_interactions": agent_data.get("total_interactions", 0),
                "total_minutes_used": float(agent_data.get("total_minutes_used", 0)),
                "last_used_at": agent_data.get("last_used_at"),
                "created_at": agent_data.get("created_at"),
                "activated_at": agent_data.get("activated_at"),
            },
        }

        # Add company info if available
        if agent_data.get("company_profile"):
            company = agent_data["company_profile"]
            formatted_data["company_info"] = {
                "company_id": company.get("id"),
                "company_name": company.get("company_name"),
                "business_category": company.get("business_category"),
                "phone_number": company.get("phone_number"),
                "website": company.get("website"),
                "timezone": company.get("timezone", "UTC"),
            }
        else:
            formatted_data["company_info"] = None

        # Add template info if available
        if agent_data.get("agent_templates"):
            template = agent_data["agent_templates"]
            formatted_data["template_info"] = {
                "template_id": template.get("id"),
                "template_name": template.get("name"),
                "template_slug": template.get("slug"),
                "agent_type": template.get("agent_type"),
                "capabilities": template.get("capabilities", []),
            }
        else:
            formatted_data["template_info"] = None

        # Add voice info and integrations
        formatted_data["voice_info"] = agent_data.get("agent_voices")
        formatted_data["integrations"] = integrations
        formatted_data["integration_count"] = len(integrations)

        return formatted_data

    async def fetch_company_integration_status(self, company_id: str) -> Dict[str, Any]:
        """
        Fetch integration status for a specific company
        """
        try:
            response = (
                self.client.table("company_integration_configurations")
                .select(
                    """
                *,
                integration_providers!inner(
                    name,
                    slug,
                    provider_type
                )
                """
                )
                .eq("company_id", company_id)
                .eq("is_active", True)
                .execute()
            )

            integrations_status = {}
            if response.data:
                for config in response.data:
                    provider = config["integration_providers"]
                    integrations_status[provider["slug"]] = {
                        "provider_name": provider["name"],
                        "provider_type": provider["provider_type"],
                        "sync_status": config.get("sync_status", "unknown"),
                        "last_sync_at": config.get("last_sync_at"),
                        "is_default": config.get("is_default", False),
                    }

            return {
                "company_id": company_id,
                "integrations_status": integrations_status,
                "total_integrations": len(integrations_status),
            }

        except Exception as e:
            print(f"❌ Error fetching company integration status: {str(e)}")
            return {
                "company_id": company_id,
                "integrations_status": {},
                "total_integrations": 0,
                "error": str(e),
            }
