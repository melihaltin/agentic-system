"""
Simplified Agent Integration Service
Service for fetching agent and integration data from the database
"""

from typing import List, Dict, Any, Optional
from src.core.database import supabase
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
            print("🔍 Fetching company agents...")

            # First, get all active agents
            agents_response = (
                self.client.table("company_agents")
                .select("*")
                .eq("is_active", True)
                .execute()
            )

            if not agents_response.data:
                print("❌ No active agents found")
                return []

            print(f"✅ Found {len(agents_response.data)} active agents")

            # Process each agent and fetch related data
            formatted_agents = []
            for agent in agents_response.data:
                formatted_agent = await self._fetch_complete_agent_data(agent)
                formatted_agents.append(formatted_agent)

            print(
                f"✅ Successfully processed {len(formatted_agents)} agents with integrations"
            )
            return formatted_agents

        except Exception as e:
            print(f"❌ Error fetching agents with integrations: {str(e)}")
            return []

    async def _fetch_complete_agent_data(
        self, agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fetch complete data for a single agent including company, template, and integrations
        """
        agent_id = agent_data["id"]
        company_id = agent_data["company_id"]
        template_id = agent_data["agent_template_id"]

        # Fetch company data
        company_info = await self._fetch_company_info(company_id)

        # Fetch template data
        template_info = await self._fetch_template_info(template_id)

        # Fetch voice data if available
        voice_info = None
        if agent_data.get("selected_voice_id"):
            voice_info = await self._fetch_voice_info(agent_data["selected_voice_id"])

        # Fetch integrations
        integrations = await self._fetch_agent_integrations(agent_id)

        # Format the complete agent data
        formatted_data = {
            "agent_id": agent_id,
            "agent_info": {
                "custom_name": agent_data.get("custom_name"),
                "language": agent_data.get("language", "en"),
                "is_configured": agent_data.get("is_configured", False),
                "total_interactions": agent_data.get("total_interactions", 0),
                "total_minutes_used": float(agent_data.get("total_minutes_used", 0)),
                "last_used_at": agent_data.get("last_used_at"),
                "created_at": agent_data.get("created_at"),
                "activated_at": agent_data.get("activated_at"),
                "configuration": agent_data.get("configuration", {}),
            },
            "company_info": company_info,
            "template_info": template_info,
            "voice_info": voice_info,
            "integrations": integrations,
            "integration_count": len(integrations),
        }

        return formatted_data

    async def _fetch_company_info(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Fetch company information"""
        try:
            response = (
                self.client.table("company_profile")
                .select("*")
                .eq("id", company_id)
                .single()
                .execute()
            )
            if response.data:
                return {
                    "company_id": response.data["id"],
                    "company_name": response.data.get("company_name"),
                    "business_category": response.data.get("business_category"),
                    "phone_number": response.data.get("phone_number"),
                    "website": response.data.get("website"),
                    "timezone": response.data.get("timezone", "UTC"),
                    "address": response.data.get("address"),
                }
        except Exception as e:
            print(f"❌ Error fetching company info for {company_id}: {str(e)}")
        return None

    async def _fetch_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Fetch agent template information"""
        try:
            response = (
                self.client.table("agent_templates")
                .select("*")
                .eq("id", template_id)
                .single()
                .execute()
            )
            if response.data:
                return {
                    "template_id": response.data["id"],
                    "template_name": response.data.get("name"),
                    "template_slug": response.data.get("slug"),
                    "agent_type": response.data.get("agent_type"),
                    "capabilities": response.data.get("capabilities", []),
                    "description": response.data.get("description"),
                }
        except Exception as e:
            print(f"❌ Error fetching template info for {template_id}: {str(e)}")
        return None

    async def _fetch_voice_info(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Fetch voice information"""
        try:
            response = (
                self.client.table("agent_voices")
                .select("*")
                .eq("id", voice_id)
                .single()
                .execute()
            )
            if response.data:
                return {
                    "voice_id": response.data["id"],
                    "name": response.data.get("name"),
                    "provider": response.data.get("provider"),
                    "voice_id_external": response.data.get("voice_id"),
                    "language": response.data.get("language"),
                }
        except Exception as e:
            print(f"❌ Error fetching voice info for {voice_id}: {str(e)}")
        return None

    async def _fetch_agent_integrations(self, agent_id: str) -> Dict[str, Any]:
        """Fetch integrations for an agent"""
        integrations = {}

        try:
            # Get integration links for this agent
            links_response = (
                self.client.table("agent_integration_links")
                .select("*")
                .eq("agent_id", agent_id)
                .execute()
            )

            if not links_response.data:
                return integrations

            for link in links_response.data:
                config_id = link["configuration_id"]

                # Get configuration details
                config_response = (
                    self.client.table("company_integration_configurations")
                    .select("*")
                    .eq("id", config_id)
                    .single()
                    .execute()
                )

                if config_response.data:
                    config = config_response.data
                    provider_id = config["provider_id"]

                    # Get provider details
                    provider_response = (
                        self.client.table("integration_providers")
                        .select("*")
                        .eq("id", provider_id)
                        .single()
                        .execute()
                    )

                    if provider_response.data:
                        provider = provider_response.data
                        provider_slug = provider.get("slug", "unknown")

                        integrations[provider_slug] = {
                            "enabled": link.get("is_enabled", False),
                            "configuration_reference": f"agent_{agent_id}_provider_{provider_slug}",
                            "provider_name": provider.get("name"),
                            "provider_type": provider.get("provider_type"),
                            "auth_type": provider.get("auth_type"),
                            "webhook_support": provider.get("webhook_support", False),
                            "webhook_url": config.get("webhook_url"),
                            "sync_status": config.get("sync_status"),
                            "last_sync_at": config.get("last_sync_at"),
                            "configuration_name": config.get("configuration_name"),
                            "permissions": link.get("permissions", {}),
                            "is_default": config.get("is_default", False),
                        }

        except Exception as e:
            print(f"❌ Error fetching integrations for agent {agent_id}: {str(e)}")

        return integrations

    async def fetch_company_integration_status(self, company_id: str) -> Dict[str, Any]:
        """
        Fetch integration status for a specific company
        """
        try:
            response = (
                self.client.table("company_integration_configurations")
                .select("*")
                .eq("company_id", company_id)
                .eq("is_active", True)
                .execute()
            )

            integrations_status = {}
            if response.data:
                for config in response.data:
                    provider_id = config["provider_id"]

                    # Get provider details
                    provider_response = (
                        self.client.table("integration_providers")
                        .select("*")
                        .eq("id", provider_id)
                        .single()
                        .execute()
                    )

                    if provider_response.data:
                        provider = provider_response.data
                        provider_slug = provider.get("slug", "unknown")

                        integrations_status[provider_slug] = {
                            "provider_name": provider.get("name"),
                            "provider_type": provider.get("provider_type"),
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
