"""
Test script to demonstrate JSON output
"""

import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.agent_integration_service_v2 import AgentIntegrationService


async def test_json_output():
    """Test and display JSON formatted output"""

    print("🔍 Testing JSON Output of Agent Integration Service")
    print("=" * 60)

    service = AgentIntegrationService()
    agents_data = await service.fetch_agents_with_integrations()

    if agents_data:
        print(f"✅ Found {len(agents_data)} agents with integrations")
        print("\n📄 JSON Output:")
        print("-" * 40)

        # Pretty print the JSON
        formatted_json = json.dumps(agents_data, indent=2, default=str)
        print(formatted_json)

        print("\n" + "=" * 60)
        print("📋 Summary:")
        for i, agent in enumerate(agents_data, 1):
            print(f"Agent {i}: {agent['agent_info'].get('custom_name', 'Unnamed')}")
            print(
                f"  Company: {agent.get('company_info', {}).get('company_name', 'Unknown')}"
            )
            print(f"  Integrations: {agent['integration_count']}")
            if agent["integrations"]:
                for provider, info in agent["integrations"].items():
                    status = "✅" if info["enabled"] else "❌"
                    print(f"    {status} {info['provider_name']} ({provider})")
    else:
        print("❌ No agents found")


if __name__ == "__main__":
    asyncio.run(test_json_output())
