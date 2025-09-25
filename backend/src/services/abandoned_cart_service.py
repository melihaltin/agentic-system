"""
Abandoned Cart Agent Service
Specialized service for handling abandoned cart recovery agents
"""

from typing import Dict, Any, List, Optional
from src.services.agent_integration_service_v2 import AgentIntegrationService
from src.services.integration_service import IntegrationService
import time
import uuid
import random


class AbandonedCartAgentService:
    """
    Service specialized for abandoned cart recovery agents
    """

    def __init__(self):
        self.agent_service = AgentIntegrationService()
        self.integration_service = IntegrationService()
        self.target_template_slug = "ecommerce-abandoned-cart"

    async def get_abandoned_cart_agents(self) -> List[Dict[str, Any]]:
        """
        Get all agents that are configured for abandoned cart recovery

        Returns:
            List of abandoned cart agents with their integration data
        """
        try:
            print("🛒 Fetching abandoned cart agents...")

            # Get all agents
            all_agents = await self.agent_service.fetch_agents_with_integrations()

            # Filter for abandoned cart agents
            abandoned_cart_agents = []
            for agent in all_agents:
                template_info = agent.get("template_info")
                if (
                    template_info
                    and template_info.get("template_slug") == self.target_template_slug
                ):
                    abandoned_cart_agents.append(agent)

            print(f"✅ Found {len(abandoned_cart_agents)} abandoned cart agents")
            return abandoned_cart_agents

        except Exception as e:
            print(f"❌ Error fetching abandoned cart agents: {str(e)}")
            return []

    async def initialize_abandoned_cart_integrations(self) -> Dict[str, Any]:
        """
        Initialize integrations specifically for abandoned cart agents

        Returns:
            Dict containing initialization results
        """
        try:
            print("🚀 Initializing abandoned cart integrations...")

            # Get abandoned cart agents
            agents = await self.get_abandoned_cart_agents()

            if not agents:
                return {
                    "success": True,
                    "message": "No abandoned cart agents found",
                    "agents": [],
                    "total_agents": 0,
                }

            # Initialize integration service
            await self.integration_service.initialize_integrations()

            # Process each agent
            processed_agents = []
            for agent in agents:
                agent_id = agent["agent_id"]
                integrations = agent.get("integrations", {})

                processed_integrations = {}
                for provider_slug, integration_data in integrations.items():
                    if integration_data.get("enabled", False):
                        # Test connection and get status
                        connection_result = (
                            await self.integration_service.test_integration_connection(
                                agent_id, provider_slug
                            )
                        )

                        processed_integrations[provider_slug] = {
                            **integration_data,
                            "connection_test": connection_result.get(
                                "connection_result", {}
                            ),
                            "ready_for_abandoned_cart": connection_result.get(
                                "success", False
                            ),
                        }

                processed_agent = {
                    **agent,
                    "processed_integrations": processed_integrations,
                    "ready_integrations_count": sum(
                        1
                        for integration in processed_integrations.values()
                        if integration.get("ready_for_abandoned_cart", False)
                    ),
                }

                processed_agents.append(processed_agent)

            return {
                "success": True,
                "message": f"Processed {len(processed_agents)} abandoned cart agents",
                "agents": processed_agents,
                "total_agents": len(processed_agents),
            }

        except Exception as e:
            print(f"❌ Error initializing abandoned cart integrations: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to initialize: {str(e)}",
                "agents": [],
                "total_agents": 0,
            }

    def generate_mock_abandoned_cart_data(
        self, provider_slug: str, company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mock abandoned cart data for testing

        Args:
            provider_slug: Platform identifier
            company_info: Company information

        Returns:
            Dict containing mock abandoned cart data
        """

        # Mock customer data
        # Mock customer data - single fixed customer
        mock_customer = {
            "id": "cust_1001",
            "email": "melih@example.com",
            "first_name": "Melih",
            "last_name": "Altin",
            "phone": "+31687611451",  # Fixed: proper international format
            "created_at": "2025-09-20T10:00:00Z",
        }

        # Mock product data
        mock_products = [
            {
                "id": f"prod_{random.randint(1000, 9999)}",
                "title": "Premium Wireless Headphones",
                "price": "199.99",
                "currency": "USD",
                "image_url": "https://example.com/headphones.jpg",
                "variant_id": f"var_{random.randint(1000, 9999)}",
            },
            {
                "id": f"prod_{random.randint(1000, 9999)}",
                "title": "Smart Fitness Watch",
                "price": "299.99",
                "currency": "USD",
                "image_url": "https://example.com/watch.jpg",
                "variant_id": f"var_{random.randint(1000, 9999)}",
            },
            {
                "id": f"prod_{random.randint(1000, 9999)}",
                "title": "Organic Coffee Beans",
                "price": "24.99",
                "currency": "USD",
                "image_url": "https://example.com/coffee.jpg",
                "variant_id": f"var_{random.randint(1000, 9999)}",
            },
        ]

        # Mock abandoned cart for single customer
        cart_products = random.sample(mock_products, random.randint(1, 3))
        total_value = sum(float(product["price"]) for product in cart_products)

        abandoned_cart = {
            "id": f"cart_{uuid.uuid4().hex[:8]}",
            "customer": mock_customer,
            "products": cart_products,
            "total_value": round(total_value, 2),
            "currency": "USD",
            "abandoned_at": "2025-09-20T10:30:00Z",
            "recovery_attempts": 0,
            "cart_url": f"https://{company_info.get('website', 'example.com')}/cart/recover/{uuid.uuid4().hex[:16]}",
            "platform": provider_slug,
            "status": "abandoned",
        }

        mock_abandoned_carts = [abandoned_cart]

        return {
            "platform": provider_slug,
            "company": company_info.get("company_name", "Unknown Company"),
            "abandoned_carts": mock_abandoned_carts,
            "total_abandoned_carts": len(mock_abandoned_carts),
            "total_recovery_value": sum(
                cart["total_value"] for cart in mock_abandoned_carts
            ),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mock_data": True,
        }

    async def fetch_abandoned_cart_data(
        self, agent_id: str, provider_slug: str
    ) -> Dict[str, Any]:
        """
        Fetch abandoned cart data from platform integration (with mock data fallback)

        Args:
            agent_id: Agent identifier
            provider_slug: Platform identifier

        Returns:
            Dict containing abandoned cart data
        """
        try:
            # For now, we'll generate mock data
            # In real implementation, this would fetch actual abandoned carts from the platform

            # Get agent info first
            all_agents = await self.get_abandoned_cart_agents()
            agent_info = None

            for agent in all_agents:
                if agent["agent_id"] == agent_id:
                    agent_info = agent
                    break

            if not agent_info:
                return {
                    "success": False,
                    "message": f"Agent {agent_id} not found or not an abandoned cart agent",
                    "data": None,
                }

            company_info = agent_info.get("company_info", {})

            # Generate mock data
            mock_data = self.generate_mock_abandoned_cart_data(
                provider_slug, company_info
            )

            return {
                "success": True,
                "message": f"Successfully fetched abandoned cart data for {provider_slug}",
                "data": mock_data,
                "agent_id": agent_id,
                "provider_slug": provider_slug,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching abandoned cart data: {str(e)}",
                "data": None,
                "agent_id": agent_id,
                "provider_slug": provider_slug,
            }

    async def create_abandoned_cart_payload(self, agent_id: str) -> Dict[str, Any]:
        """
        Create complete payload for abandoned cart recovery

        Args:
            agent_id: Agent identifier

        Returns:
            Dict containing complete payload for external API
        """
        try:
            print(f"📦 Creating abandoned cart payload for agent {agent_id}")

            # Get agent information
            all_agents = await self.get_abandoned_cart_agents()
            agent_info = None

            for agent in all_agents:
                if agent["agent_id"] == agent_id:
                    agent_info = agent
                    break

            if not agent_info:
                return {
                    "success": False,
                    "message": f"Agent {agent_id} not found or not an abandoned cart agent",
                    "payload": None,
                }

            # Get integration data for all platforms
            integrations = agent_info.get("integrations", {})
            platform_data = {}

            for provider_slug, integration_data in integrations.items():
                if integration_data.get("enabled", False):
                    print(f"   Fetching data from {provider_slug}...")

                    cart_data_result = await self.fetch_abandoned_cart_data(
                        agent_id, provider_slug
                    )

                    if cart_data_result["success"]:
                        platform_data[provider_slug] = cart_data_result["data"]
                    else:
                        print(
                            f"   ❌ Failed to fetch data from {provider_slug}: {cart_data_result['message']}"
                        )

            # Create comprehensive payload
            payload = {
                "agent": {
                    "id": agent_info["agent_id"],
                    "name": agent_info["agent_info"].get(
                        "custom_name", "Abandoned Cart Agent"
                    ),
                    "type": "abandoned_cart_recovery",
                    "template_slug": self.target_template_slug,
                    "is_configured": agent_info["agent_info"].get(
                        "is_configured", False
                    ),
                    "total_interactions": agent_info["agent_info"].get(
                        "total_interactions", 0
                    ),
                    "selected_voice_id": agent_info.get("voice_info", {}).get(
                        "voice_id_external"
                    ),
                    "language": agent_info.get("agent_info", {}).get("language", "en"),
                    "tts_provider": agent_info.get("voice_info", {}).get(
                        "provider", "elevenlabs"
                    ),
                },
                "company": {
                    "id": agent_info.get("company_info", {}).get("company_id"),
                    "name": agent_info.get("company_info", {}).get("company_name"),
                    "business_category": agent_info.get("company_info", {}).get(
                        "business_category"
                    ),
                    "phone_number": agent_info.get("company_info", {}).get(
                        "phone_number"
                    ),
                    "website": agent_info.get("company_info", {}).get("website"),
                    "timezone": agent_info.get("company_info", {}).get(
                        "timezone", "UTC"
                    ),
                },
                "voice_config": agent_info.get("voice_info"),
                "platforms": platform_data,
                "summary": {
                    "total_platforms": len(platform_data),
                    "total_abandoned_carts": sum(
                        data.get("total_abandoned_carts", 0)
                        for data in platform_data.values()
                    ),
                    "total_recovery_value": sum(
                        data.get("total_recovery_value", 0)
                        for data in platform_data.values()
                    ),
                    "currencies": list(
                        set(
                            cart.get("currency", "USD")
                            for data in platform_data.values()
                            for cart in data.get("abandoned_carts", [])
                        )
                    ),
                },
                "metadata": {
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "payload_version": "1.0",
                    "service": "abandoned_cart_recovery",
                },
            }

            print(
                f"✅ Created payload with {payload['summary']['total_abandoned_carts']} abandoned carts from {payload['summary']['total_platforms']} platforms"
            )

            return {
                "success": True,
                "message": "Successfully created abandoned cart payload",
                "payload": payload,
                "agent_id": agent_id,
            }

        except Exception as e:
            print(f"❌ Error creating payload: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating payload: {str(e)}",
                "payload": None,
                "agent_id": agent_id,
            }

    async def send_to_external_api(
        self, payload: Dict[str, Any], api_url: str, api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send abandoned cart payload to external API

        Args:
            payload: Complete abandoned cart payload
            api_url: External API endpoint URL
            api_key: Optional API key for authentication

        Returns:
            Dict containing API response results
        """
        try:
            import httpx

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "AbandonedCartAgent/1.0",
            }

            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            print(f"📤 Sending payload to external API: {api_url}")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url, json=payload, headers=headers, timeout=30.0
                )

                return {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "response_data": (
                        response.json()
                        if response.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else response.text
                    ),
                    "message": f"API request completed with status {response.status_code}",
                    "api_url": api_url,
                }

        except httpx.TimeoutException:
            return {
                "success": False,
                "status_code": None,
                "response_data": None,
                "message": "API request timed out",
                "api_url": api_url,
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response_data": None,
                "message": f"API request failed: {str(e)}",
                "api_url": api_url,
            }
