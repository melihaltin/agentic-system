import httpx
import logging
from typing import List, Dict, Any, Optional

from src.core.database import supabase


logger = logging.getLogger(__name__)


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
                    print(f"⚠️ Skipping invalid config for {provider_slug}: {config}")
                    continue

                print(f"🔍 Processing integration for provider: {provider_slug}")

                # Get provider info
                provider_result = (
                    supabase.table("integration_providers")
                    .select("id, required_fields")
                    .eq("slug", provider_slug)
                    .execute()
                )

                if not provider_result.data:
                    print(f"❌ Provider not found for slug: {provider_slug}")
                    continue

                print(f"✅ Found provider: {provider_result.data[0]}")

                provider_id = provider_result.data[0]["id"]
                print(f"🆔 Using provider_id: {provider_id}")

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
                    print(f"🔄 Using existing configuration: {configuration_id}")
                else:
                    # Create new configuration
                    new_config = {
                        "company_id": company_id,
                        "provider_id": provider_id,
                        "configuration_name": f"{provider_slug}_config",
                        "is_active": True,
                        "is_default": True,
                    }

                    print(f"🆕 Creating new configuration: {new_config}")

                    create_result = (
                        supabase.table("company_integration_configurations")
                        .insert(new_config)
                        .execute()
                    )

                    if create_result.data:
                        configuration_id = create_result.data[0]["id"]
                        print(f"✅ Created new configuration: {configuration_id}")
                    else:
                        print(f"❌ Failed to create configuration: {create_result}")
                        continue

                # Save encrypted credentials
                print(f"💾 Saving credentials for config {configuration_id}: {config}")
                await IntegrationService._save_encrypted_credentials(
                    configuration_id, config
                )

                # Link agent to integration
                print(
                    f"🔗 Linking agent {agent_id} to configuration {configuration_id}"
                )
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
            print(f"🗑️ Deleting existing credentials for config: {configuration_id}")
            # Delete existing credentials
            delete_result = (
                supabase.table("integration_credentials")
                .delete()
                .eq("configuration_id", configuration_id)
                .execute()
            )
            print(f"🗑️ Delete result: {delete_result}")

            # Save new credentials
            for key, value in config.items():
                if value and isinstance(value, str):
                    credential_data = {
                        "configuration_id": configuration_id,
                        "credential_key": key,
                        "encrypted_value": value,  # In production, this should be encrypted
                    }

                    print(f"💾 Saving credential: {key} for config {configuration_id}")
                    insert_result = (
                        supabase.table("integration_credentials")
                        .insert(credential_data)
                        .execute()
                    )
                    print(f"💾 Insert result: {insert_result}")
                else:
                    print(f"⚠️ Skipping invalid credential: {key} = {value}")

        except Exception as e:
            logger.error(f"Error saving encrypted credentials: {e}")
            print(f"❌ Error in _save_encrypted_credentials: {e}")
            raise

    @staticmethod
    async def _link_agent_to_integration(agent_id: str, configuration_id: str):
        """Link agent to integration configuration"""
        try:
            print(
                f"🔍 Checking existing link for agent {agent_id} and config {configuration_id}"
            )
            # Check if link already exists
            existing_link = (
                supabase.table("agent_integration_links")
                .select("id")
                .eq("agent_id", agent_id)
                .eq("configuration_id", configuration_id)
                .execute()
            )

            print(f"🔍 Existing link result: {existing_link}")

            if not existing_link.data:
                # Create new link
                link_data = {
                    "agent_id": agent_id,
                    "configuration_id": configuration_id,
                    "is_enabled": True,
                    "permissions": {},
                }

                print(f"🆕 Creating new link: {link_data}")
                link_result = (
                    supabase.table("agent_integration_links")
                    .insert(link_data)
                    .execute()
                )
                print(f"✅ Link created: {link_result}")
            else:
                # Update existing link to enabled
                print(f"🔄 Updating existing link to enabled")
                update_result = (
                    supabase.table("agent_integration_links")
                    .update({"is_enabled": True})
                    .eq("id", existing_link.data[0]["id"])
                    .execute()
                )
                print(f"✅ Link updated: {update_result}")

        except Exception as e:
            logger.error(f"Error linking agent to integration: {e}")
            print(f"❌ Error in _link_agent_to_integration: {e}")
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
