"""
Integration Service
High-level service for managing and executing platform integrations
"""

from typing import Dict, Any, List, Optional
from src.services.agent_integration_service_v2 import AgentIntegrationService
from src.services.integration_manager import IntegrationManager
from src.core.integration_interface import BaseIntegrationAdapter, APIResponse


class IntegrationService:
    """
    Service class for handling platform integrations
    """

    def __init__(self):
        self.agent_service = AgentIntegrationService()
        self.integration_manager = IntegrationManager()
        self._loaded_agents_cache: Optional[List[Dict[str, Any]]] = None

    async def initialize_integrations(self) -> Dict[str, Any]:
        """
        Initialize all integrations by loading agent data and creating adapters

        Returns:
            Dict containing initialization results
        """
        try:
            print("🚀 Initializing platform integrations...")

            # Fetch agent data
            agents_data = await self.agent_service.fetch_agents_with_integrations()
            if not agents_data:
                return {
                    "success": False,
                    "message": "No agents with integrations found",
                    "total_agents": 0,
                    "total_integrations": 0,
                }

            # Cache agents data
            self._loaded_agents_cache = agents_data

            # Load all integrations
            loaded_integrations = self.integration_manager.load_all_integrations(
                agents_data
            )

            # Count total integrations
            total_integrations = sum(
                len(adapters) for adapters in loaded_integrations.values()
            )

            print(
                f"✅ Successfully initialized {total_integrations} integrations for {len(agents_data)} agents"
            )

            return {
                "success": True,
                "message": f"Successfully initialized {total_integrations} integrations",
                "total_agents": len(agents_data),
                "total_integrations": total_integrations,
                "loaded_integrations": {
                    agent_id: len(adapters)
                    for agent_id, adapters in loaded_integrations.items()
                },
            }

        except Exception as e:
            print(f"❌ Error initializing integrations: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to initialize integrations: {str(e)}",
                "total_agents": 0,
                "total_integrations": 0,
            }

    async def test_integration_connection(
        self, agent_id: str, provider_slug: str
    ) -> Dict[str, Any]:
        """
        Test connection for a specific integration

        Args:
            agent_id: Agent identifier
            provider_slug: Platform identifier

        Returns:
            Dict containing test results
        """
        try:
            adapter = self.integration_manager.get_integration(agent_id, provider_slug)
            if not adapter:
                return {
                    "success": False,
                    "message": f"Integration {provider_slug} not found for agent {agent_id}",
                    "agent_id": agent_id,
                    "provider_slug": provider_slug,
                }

            # Test connection
            test_result = await adapter.test_connection()

            return {
                "success": test_result.success,
                "message": "Connection test completed",
                "agent_id": agent_id,
                "provider_slug": provider_slug,
                "provider_name": adapter.provider_name,
                "connection_result": {
                    "success": test_result.success,
                    "error_message": test_result.error_message,
                    "response_time": test_result.response_time,
                    "status_code": test_result.status_code,
                    "data": test_result.data,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error testing connection: {str(e)}",
                "agent_id": agent_id,
                "provider_slug": provider_slug,
            }

    async def fetch_platform_data(
        self,
        agent_id: str,
        provider_slug: str,
        data_type: str,
        limit: int = 50,
        offset: int = 0,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch data from a platform integration

        Args:
            agent_id: Agent identifier
            provider_slug: Platform identifier
            data_type: Type of data to fetch (products, orders, customers)
            limit: Maximum number of items to fetch
            offset: Number of items to skip
            query: Search query (for search operations)

        Returns:
            Dict containing fetched data
        """
        try:
            adapter = self.integration_manager.get_integration(agent_id, provider_slug)
            if not adapter:
                return {
                    "success": False,
                    "message": f"Integration {provider_slug} not found for agent {agent_id}",
                    "agent_id": agent_id,
                    "provider_slug": provider_slug,
                    "data_type": data_type,
                }

            # Execute the appropriate method based on data type
            result: APIResponse

            if data_type == "products" and query:
                result = await adapter.search_products(query, limit)
            elif data_type == "products":
                result = await adapter.get_products(limit, offset)
            elif data_type == "orders":
                result = await adapter.get_orders(limit, offset)
            elif data_type == "customers":
                result = await adapter.get_customers(limit, offset)
            else:
                return {
                    "success": False,
                    "message": f"Unsupported data type: {data_type}",
                    "agent_id": agent_id,
                    "provider_slug": provider_slug,
                    "data_type": data_type,
                }

            return {
                "success": result.success,
                "message": f"Data fetch completed for {data_type}",
                "agent_id": agent_id,
                "provider_slug": provider_slug,
                "provider_name": adapter.provider_name,
                "data_type": data_type,
                "query": query,
                "limit": limit,
                "offset": offset,
                "result": {
                    "success": result.success,
                    "data": result.data,
                    "error_message": result.error_message,
                    "response_time": result.response_time,
                    "status_code": result.status_code,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching {data_type}: {str(e)}",
                "agent_id": agent_id,
                "provider_slug": provider_slug,
                "data_type": data_type,
            }

    async def get_integration_status(
        self, agent_id: str, provider_slug: str
    ) -> Dict[str, Any]:
        """
        Get status information for an integration

        Args:
            agent_id: Agent identifier
            provider_slug: Platform identifier

        Returns:
            Dict containing status information
        """
        try:
            adapter = self.integration_manager.get_integration(agent_id, provider_slug)
            if not adapter:
                return {
                    "success": False,
                    "message": f"Integration {provider_slug} not found for agent {agent_id}",
                    "agent_id": agent_id,
                    "provider_slug": provider_slug,
                }

            # Get integration status
            status = await adapter.get_integration_status()

            return {
                "success": True,
                "message": "Integration status retrieved",
                "agent_id": agent_id,
                "provider_slug": provider_slug,
                "status": status,
                "webhook_config": adapter.get_webhook_config(),
                "supported_events": adapter.get_supported_webhook_events(),
                "credentials_valid": adapter.validate_credentials(),
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting integration status: {str(e)}",
                "agent_id": agent_id,
                "provider_slug": provider_slug,
            }

    def get_available_providers(self) -> List[str]:
        """
        Get list of available integration providers

        Returns:
            List of provider slugs
        """
        return self.integration_manager.factory.get_available_providers()

    def get_active_integrations_summary(self) -> Dict[str, Any]:
        """
        Get summary of all active integrations

        Returns:
            Dict containing integrations summary
        """
        active_integrations = self.integration_manager.get_active_integrations()

        summary = {
            "total_active": len(active_integrations),
            "by_provider": {},
            "by_agent": {},
            "integrations": [],
        }

        for key, adapter in active_integrations.items():
            agent_id, provider_slug = key.split("_", 1)

            # Count by provider
            if provider_slug not in summary["by_provider"]:
                summary["by_provider"][provider_slug] = 0
            summary["by_provider"][provider_slug] += 1

            # Count by agent
            if agent_id not in summary["by_agent"]:
                summary["by_agent"][agent_id] = 0
            summary["by_agent"][agent_id] += 1

            # Add to integrations list
            summary["integrations"].append(
                {
                    "agent_id": agent_id,
                    "provider_slug": provider_slug,
                    "provider_name": adapter.provider_name,
                    "is_enabled": adapter.is_enabled,
                    "credentials_valid": adapter.validate_credentials(),
                }
            )

        return summary

    async def reload_integrations(self) -> Dict[str, Any]:
        """
        Reload all integrations (clear cache and reinitialize)

        Returns:
            Dict containing reload results
        """
        print("🔄 Reloading all integrations...")

        # Clear existing integrations
        self.integration_manager.clear_integrations()
        self._loaded_agents_cache = None

        # Reinitialize
        return await self.initialize_integrations()
