"""
Integration Test Script
Test the complete integration system with real data
"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.integration_service import IntegrationService


async def test_integration_system():
    """Test the complete integration system"""

    print("🚀 Testing Platform Integration System")
    print("=" * 60)

    # Initialize integration service
    service = IntegrationService()

    # Step 1: Initialize integrations
    print("\n📦 Step 1: Initializing integrations...")
    init_result = await service.initialize_integrations()

    if not init_result["success"]:
        print(f"❌ Failed to initialize: {init_result['message']}")
        return

    print(
        f"✅ Initialized {init_result['total_integrations']} integrations for {init_result['total_agents']} agents"
    )

    # Step 2: Get available providers
    print("\n🔧 Step 2: Available providers...")
    providers = service.get_available_providers()
    print(f"✅ Available providers: {', '.join(providers)}")

    # Step 3: Get integrations summary
    print("\n📊 Step 3: Active integrations summary...")
    summary = service.get_active_integrations_summary()
    print(f"✅ Total active integrations: {summary['total_active']}")

    if summary["integrations"]:
        print("\n🔗 Active integrations:")
        for integration in summary["integrations"]:
            agent_id = integration["agent_id"][:8] + "..."  # Shortened for display
            print(
                f"   🤖 Agent {agent_id} → {integration['provider_name']} ({integration['provider_slug']})"
            )
            print(f"      Enabled: {'✅' if integration['is_enabled'] else '❌'}")
            print(
                f"      Credentials: {'✅' if integration['credentials_valid'] else '❌'}"
            )

    # Step 4: Test specific integrations
    print("\n🧪 Step 4: Testing integrations...")
    for integration in summary["integrations"]:
        agent_id = integration["agent_id"]
        provider_slug = integration["provider_slug"]

        print(
            f"\n   Testing {integration['provider_name']} for agent {agent_id[:8]}..."
        )

        # Test connection
        connection_result = await service.test_integration_connection(
            agent_id, provider_slug
        )
        if connection_result["success"]:
            conn_data = connection_result["connection_result"]
            if conn_data["success"]:
                print(
                    f"   ✅ Connection test passed ({conn_data['response_time']:.2f}s)"
                )
                if conn_data.get("data"):
                    print(
                        f"      Store: {conn_data['data'].get('shop_name', 'Unknown')}"
                    )
            else:
                print(
                    f"   ❌ Connection test failed: {conn_data.get('error_message', 'Unknown error')}"
                )

        # Get integration status
        status_result = await service.get_integration_status(agent_id, provider_slug)
        if status_result["success"]:
            status = status_result["status"]
            print(f"   📊 Status: {status.get('connection_status', 'unknown')}")

            webhook_config = status_result.get("webhook_config")
            if webhook_config:
                print(f"   🔗 Webhook configured: {webhook_config['webhook_url']}")

            events = status_result.get("supported_events", [])
            print(f"   📡 Supported events: {len(events)}")

    # Step 5: Test data fetching (if we have working integrations)
    print("\n📊 Step 5: Testing data fetching...")

    for integration in summary["integrations"]:
        if not integration["credentials_valid"]:
            continue

        agent_id = integration["agent_id"]
        provider_slug = integration["provider_slug"]

        print(f"\n   Fetching data from {integration['provider_name']}...")

        # Try to fetch products (limit to 5 for testing)
        products_result = await service.fetch_platform_data(
            agent_id=agent_id,
            provider_slug=provider_slug,
            data_type="products",
            limit=5,
            offset=0,
        )

        if products_result["success"] and products_result["result"]["success"]:
            data = products_result["result"]["data"]
            products = data.get("products", [])
            print(f"   ✅ Products fetched: {len(products)} items")
            if products:
                print(f"      Sample product: {products[0].get('title', 'Unknown')}")
        else:
            error_msg = products_result.get("message", "Unknown error")
            if products_result.get("result"):
                error_msg = products_result["result"].get("error_message", error_msg)
            print(f"   ❌ Products fetch failed: {error_msg}")

    print("\n" + "=" * 60)
    print("🎉 Integration system test completed!")


if __name__ == "__main__":
    asyncio.run(test_integration_system())
