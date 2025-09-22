"""
Agent Integration Polling Service
Polls agent integration data periodically and displays results
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from src.services.agent_integration_service_v2 import AgentIntegrationService
from src.services.abandoned_cart_service import AbandonedCartAgentService


class AgentIntegrationPoller:
    """
    Polling service for agent integrations
    """

    def __init__(self, polling_interval: int = 30):
        """
        Initialize the poller

        Args:
            polling_interval: Time between polls in seconds (default: 30)
        """
        self.polling_interval = polling_interval
        self.service = AgentIntegrationService()
        self.abandoned_cart_service = AbandonedCartAgentService()
        self.is_running = False
        self.last_poll_time = None
        self.poll_count = 0

    async def start_polling(self):
        """
        Start the polling loop
        """
        print("🚀 Starting Agent Integration Polling Service...")
        print(f"⏱️  Polling interval: {self.polling_interval} seconds")
        print("-" * 80)

        self.is_running = True

        while self.is_running:
            try:
                await self._perform_poll()
                await asyncio.sleep(self.polling_interval)
            except KeyboardInterrupt:
                print("\n⏹️  Polling stopped by user")
                break
            except Exception as e:
                print(f"❌ Polling error: {str(e)}")
                await asyncio.sleep(5)  # Wait 5 seconds before retrying

    async def stop_polling(self):
        """
        Stop the polling loop
        """
        self.is_running = False
        print("⏹️  Polling service stopped")

    async def _perform_poll(self):
        """
        Perform a single poll operation
        """
        self.poll_count += 1
        self.last_poll_time = datetime.now()

        print(
            f"\n📊 Poll #{self.poll_count} - {self.last_poll_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 80)

        # Fetch agents with integrations
        agents_data = await self.service.fetch_agents_with_integrations()

        if not agents_data:
            print("📭 No active agents with integrations found")
            return

        # Display results
        await self._display_polling_results(agents_data)

        # Process abandoned cart agents
        await self._process_abandoned_cart_agents()

    async def _display_polling_results(self, agents_data: List[Dict[str, Any]]):
        """
        Display polling results in a formatted way
        """
        print(f"🏢 Found {len(agents_data)} active agents with integrations")
        print("-" * 80)

        for i, agent in enumerate(agents_data, 1):
            await self._display_agent_info(agent, i)
            print("-" * 40)

    async def _display_agent_info(self, agent_data: Dict[str, Any], index: int):
        """
        Display information for a single agent
        """
        company_info = agent_data["company_info"]
        agent_info = agent_data["agent_info"]
        template_info = agent_data["template_info"]
        integrations = agent_data["integrations"]

        print(f"🤖 Agent #{index}: {agent_info.get('custom_name', 'Unnamed Agent')}")
        print(f"   🏢 Company: {company_info['company_name']}")
        print(f"   📱 Business: {company_info.get('business_category', 'Unknown')}")
        print(
            f"   🎭 Template: {template_info['template_name']} ({template_info['agent_type']})"
        )
        print(
            f"   📊 Stats: {agent_info['total_interactions']} interactions, {agent_info['total_minutes_used']} minutes"
        )
        print(f"   🔧 Configured: {'✅' if agent_info['is_configured'] else '❌'}")

        if integrations:
            print(f"   🔗 Integrations ({len(integrations)}):")
            for provider_slug, integration_info in integrations.items():
                status_icon = "✅" if integration_info["enabled"] else "❌"
                sync_status = integration_info.get("sync_status", "unknown")
                print(
                    f"      {status_icon} {integration_info['provider_name']} ({provider_slug})"
                )
                print(
                    f"         • Type: {integration_info.get('provider_type', 'Unknown')}"
                )
                print(
                    f"         • Auth: {integration_info.get('auth_type', 'Unknown')}"
                )
                print(f"         • Sync Status: {sync_status}")
                print(
                    f"         • Webhook: {'✅' if integration_info.get('webhook_support') else '❌'}"
                )
                if integration_info.get("webhook_url"):
                    print(f"         • Webhook URL: {integration_info['webhook_url']}")
                if integration_info.get("last_sync_at"):
                    print(f"         • Last Sync: {integration_info['last_sync_at']}")
        else:
            print(f"   🔗 Integrations: None configured")

    async def _process_abandoned_cart_agents(self):
        """
        Process abandoned cart agents and send API requests
        """
        try:
            print("\n🛒 Processing Abandoned Cart Agents...")
            print("=" * 50)

            # Get abandoned cart agents
            abandoned_cart_agents = (
                await self.abandoned_cart_service.get_abandoned_cart_agents()
            )

            if not abandoned_cart_agents:
                print("📭 No abandoned cart agents found")
                return

            print(f"🎯 Found {len(abandoned_cart_agents)} abandoned cart agents")

            total_carts_processed = 0
            total_recovery_value = 0.0

            for agent in abandoned_cart_agents:
                try:
                    # Extract agent information from the nested structure
                    agent_info = agent.get("agent_info", {})
                    company_info = agent.get("company_info", {})
                    integrations = agent.get("integrations", {})

                    agent_name = agent_info.get("custom_name", "Unnamed Agent")
                    company_name = company_info.get("company_name", "Unknown Company")

                    print(f"\n🤖 Processing Agent: {agent_name}")
                    print(f"   🏢 Company: {company_name}")

                    # Process each integration platform for this agent
                    if integrations:
                        for platform_slug, integration_info in integrations.items():
                            try:
                                platform_name = integration_info.get(
                                    "provider_name", platform_slug
                                )
                                print(
                                    f"   📱 Platform: {platform_name} ({platform_slug})"
                                )

                                # Generate mock data for this platform
                                mock_data = self.abandoned_cart_service.generate_mock_abandoned_cart_data(
                                    platform_slug, company_info
                                )

                                if mock_data and mock_data.get("abandoned_carts"):
                                    carts = mock_data["abandoned_carts"]
                                    recovery_value = sum(
                                        cart["total_value"] for cart in carts
                                    )

                                    print(
                                        f"      🛒 Generated {len(carts)} abandoned carts"
                                    )
                                    print(
                                        f"      💰 Recovery value: ${recovery_value:.2f}"
                                    )

                                    # Create enhanced payload
                                    payload_result = await self.abandoned_cart_service.create_abandoned_cart_payload(
                                        agent["agent_id"]
                                    )

                                    if not payload_result.get("success"):
                                        print(
                                            f"      ❌ Failed to create payload: {payload_result.get('message')}"
                                        )
                                        continue

                                    payload = payload_result["payload"]

                                    print(
                                        f"      📨 Payload: {json.dumps(payload, indent=2)}"
                                    )  # Debug print

                                    # Send to external API (using HTTP not HTTPS for localhost)
                                    api_response = await self.abandoned_cart_service.send_to_external_api(
                                        payload, "http://localhost:5000/start-call"
                                    )

                                    if (
                                        api_response
                                        and api_response.get("status_code") == 200
                                    ):
                                        print(f"      ✅ Successfully sent to API")
                                        response_data = api_response.get(
                                            "response_data", {}
                                        )
                                        if response_data.get("thread_id"):
                                            print(
                                                f"      🧵 Thread ID: {response_data['thread_id']}"
                                            )
                                        total_carts_processed += len(carts)
                                        total_recovery_value += recovery_value
                                    else:
                                        print(
                                            f"      ❌ Failed to send to API: {api_response}"
                                        )
                                else:
                                    print(
                                        f"      📭 No abandoned carts found for {platform_name}"
                                    )

                            except Exception as platform_error:
                                print(
                                    f"      ❌ Error processing platform {platform_slug}: {str(platform_error)}"
                                )
                    else:
                        print(f"   📭 No integrations configured for this agent")

                except Exception as agent_error:
                    print(f"   ❌ Error processing agent: {str(agent_error)}")

            print(f"\n📊 Polling Summary:")
            print(f"   🛒 Total carts processed: {total_carts_processed}")
            print(f"   💰 Total recovery value: ${total_recovery_value:.2f}")
            print("=" * 50)

        except Exception as e:
            print(f"❌ Error in abandoned cart processing: {str(e)}")

    async def poll_once(self):
        """
        Perform a single poll (useful for testing)
        """
        print("🔍 Performing single poll...")
        await self._perform_poll()

    def get_status(self) -> Dict[str, Any]:
        """
        Get current polling status
        """
        return {
            "is_running": self.is_running,
            "polling_interval": self.polling_interval,
            "poll_count": self.poll_count,
            "last_poll_time": (
                self.last_poll_time.isoformat() if self.last_poll_time else None
            ),
        }


# Standalone polling function for direct execution
async def run_agent_integration_polling(interval: int = 30):
    """
    Run agent integration polling as a standalone service

    Args:
        interval: Polling interval in seconds
    """
    poller = AgentIntegrationPoller(polling_interval=interval)
    await poller.start_polling()


if __name__ == "__main__":
    # Run polling service directly
    asyncio.run(run_agent_integration_polling(interval=30))
