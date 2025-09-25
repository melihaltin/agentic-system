"""
Integration Factory and Manager
Manages dynamic loading and execution of platform integrations
"""

from typing import Dict, Any, Optional, Type, List
from src.core.integration_interface import (
    BaseIntegrationAdapter,
    IntegrationConfig,
    IntegrationCredentials,
)
from src.integrations.shopify_adapter import ShopifyAdapter
from src.integrations.woocommerce_adapter import WooCommerceAdapter


class IntegrationFactory:
    """
    Factory class for creating platform integration adapters
    """

    # Registry of available adapters
    _adapters: Dict[str, Type[BaseIntegrationAdapter]] = {
        "shopify": ShopifyAdapter,
        "woocommerce": WooCommerceAdapter,
    }

    @classmethod
    def register_adapter(
        cls, provider_slug: str, adapter_class: Type[BaseIntegrationAdapter]
    ):
        """
        Register a new integration adapter

        Args:
            provider_slug: Unique identifier for the platform
            adapter_class: The adapter class implementing BaseIntegrationAdapter
        """
        cls._adapters[provider_slug] = adapter_class

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available integration providers

        Returns:
            List of provider slugs
        """
        return list(cls._adapters.keys())

    @classmethod
    def create_adapter(
        cls, provider_slug: str, config: IntegrationConfig
    ) -> Optional[BaseIntegrationAdapter]:
        """
        Create an integration adapter instance

        Args:
            provider_slug: The platform identifier
            config: Integration configuration

        Returns:
            Adapter instance or None if provider not found
        """
        adapter_class = cls._adapters.get(provider_slug)
        if adapter_class:
            return adapter_class(config)
        return None

    @classmethod
    def is_provider_supported(cls, provider_slug: str) -> bool:
        """
        Check if a provider is supported

        Args:
            provider_slug: The platform identifier

        Returns:
            True if supported, False otherwise
        """
        return provider_slug in cls._adapters


class IntegrationManager:
    """
    High-level manager for handling multiple platform integrations
    """

    def __init__(self):
        self.factory = IntegrationFactory()
        self._active_integrations: Dict[str, BaseIntegrationAdapter] = {}

    def create_integration_config(
        self,
        agent_data: Dict[str, Any],
        provider_slug: str,
        integration_data: Dict[str, Any],
    ) -> Optional[IntegrationConfig]:
        """
        Create integration config from agent and integration data

        Args:
            agent_data: Agent information from polling service
            provider_slug: Platform identifier
            integration_data: Integration configuration data

        Returns:
            IntegrationConfig instance or None if data is invalid
        """
        try:
            # Extract credentials from agent configuration
            agent_config = agent_data.get("agent_info", {}).get("configuration", {})
            platform_config = agent_config.get(provider_slug, {})

            # Create credentials object
            credentials = IntegrationCredentials(
                api_key=platform_config.get("apiKey")
                or platform_config.get("consumer_key"),
                api_secret=platform_config.get("apiSecret")
                or platform_config.get("consumer_secret"),
                store_url=platform_config.get("storeUrl")
                or platform_config.get("store_url"),
                access_token=platform_config.get("accessToken")
                or platform_config.get("access_token"),
                webhook_secret=platform_config.get("webhookSecret"),
                additional_fields=platform_config.get("additional_fields", {}),
            )

            # Create integration config
            config = IntegrationConfig(
                provider_slug=provider_slug,
                provider_name=integration_data.get("provider_name", provider_slug),
                agent_id=agent_data["agent_id"],
                company_id=agent_data.get("company_info", {}).get("company_id", ""),
                credentials=credentials,
                webhook_url=integration_data.get("webhook_url"),
                is_enabled=integration_data.get("enabled", True),
                settings=integration_data.get("permissions", {}),
            )

            return config

        except Exception as e:
            print(f"❌ Error creating integration config for {provider_slug}: {str(e)}")
            return None

    def load_integration(
        self, agent_data: Dict[str, Any], provider_slug: str
    ) -> Optional[BaseIntegrationAdapter]:
        """
        Load an integration adapter for an agent and platform

        Args:
            agent_data: Agent information from polling service
            provider_slug: Platform identifier

        Returns:
            Loaded adapter instance or None if failed
        """
        try:
            # Check if provider is supported
            if not self.factory.is_provider_supported(provider_slug):
                print(f"❌ Provider {provider_slug} is not supported")
                return None

            # Get integration data for this provider
            integrations = agent_data.get("integrations", {})
            integration_data = integrations.get(provider_slug)

            if not integration_data:
                print(f"❌ No integration data found for {provider_slug}")
                return None

            # Create configuration
            config = self.create_integration_config(
                agent_data, provider_slug, integration_data
            )
            if not config:
                print(f"❌ Failed to create configuration for {provider_slug}")
                return None

            # Create adapter
            adapter = self.factory.create_adapter(provider_slug, config)
            if not adapter:
                print(f"❌ Failed to create adapter for {provider_slug}")
                return None

            # Store active integration
            integration_key = f"{agent_data['agent_id']}_{provider_slug}"
            self._active_integrations[integration_key] = adapter

            print(
                f"✅ Successfully loaded {provider_slug} integration for agent {agent_data['agent_id']}"
            )
            return adapter

        except Exception as e:
            print(f"❌ Error loading integration {provider_slug}: {str(e)}")
            return None

    def get_integration(
        self, agent_id: str, provider_slug: str
    ) -> Optional[BaseIntegrationAdapter]:
        """
        Get an active integration adapter

        Args:
            agent_id: Agent identifier
            provider_slug: Platform identifier

        Returns:
            Adapter instance or None if not found
        """
        integration_key = f"{agent_id}_{provider_slug}"
        return self._active_integrations.get(integration_key)

    def load_all_integrations(
        self, agents_data: List[Dict[str, Any]]
    ) -> Dict[str, List[BaseIntegrationAdapter]]:
        """
        Load all integrations for all agents

        Args:
            agents_data: List of agent data from polling service

        Returns:
            Dict mapping agent IDs to their loaded adapters
        """
        loaded_integrations = {}

        for agent_data in agents_data:
            agent_id = agent_data["agent_id"]
            agent_integrations = []

            # Load each integration for this agent
            for provider_slug in agent_data.get("integrations", {}):
                adapter = self.load_integration(agent_data, provider_slug)
                if adapter:
                    agent_integrations.append(adapter)

            loaded_integrations[agent_id] = agent_integrations
            print(f"🤖 Agent {agent_id}: Loaded {len(agent_integrations)} integrations")

        return loaded_integrations

    def get_active_integrations(self) -> Dict[str, BaseIntegrationAdapter]:
        """
        Get all active integrations

        Returns:
            Dict of active integrations
        """
        return self._active_integrations.copy()

    def clear_integrations(self):
        """Clear all active integrations"""
        self._active_integrations.clear()
        print("🧹 Cleared all active integrations")
