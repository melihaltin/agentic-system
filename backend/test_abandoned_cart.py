"""
Abandoned Cart Test Script
Test the abandoned cart recovery system end-to-end
"""
import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.abandoned_cart_service import AbandonedCartAgentService


async def test_abandoned_cart_system():
    """Test the complete abandoned cart system"""
    
    print("🛒 Testing Abandoned Cart Recovery System")
    print("=" * 60)
    
    service = AbandonedCartAgentService()
    
    # Step 1: Get abandoned cart agents
    print("\n📋 Step 1: Getting abandoned cart agents...")
    agents = await service.get_abandoned_cart_agents()
    
    if not agents:
        print("❌ No abandoned cart agents found")
        print("ℹ️  Make sure you have agents with 'ecommerce-abandoned-cart' template")
        return
    
    print(f"✅ Found {len(agents)} abandoned cart agents:")
    for agent in agents:
        agent_name = agent["agent_info"].get("custom_name", "Unnamed")
        company_name = agent.get("company_info", {}).get("company_name", "Unknown")
        integrations_count = agent.get("integration_count", 0)
        print(f"   🤖 {agent_name} ({company_name}) - {integrations_count} integrations")
    
    # Step 2: Initialize integrations
    print("\n🔧 Step 2: Initializing abandoned cart integrations...")
    init_result = await service.initialize_abandoned_cart_integrations()
    
    if init_result["success"]:
        print(f"✅ Initialized integrations for {init_result['total_agents']} agents")
    else:
        print(f"❌ Failed to initialize: {init_result['message']}")
        return
    
    # Step 3: Test with first agent
    if agents:
        test_agent = agents[0]
        agent_id = test_agent["agent_id"]
        agent_name = test_agent["agent_info"].get("custom_name", "Unnamed")
        
        print(f"\n🧪 Step 3: Testing with agent '{agent_name}' ({agent_id[:8]}...)")
        
        # Test data fetching for each integration
        integrations = test_agent.get("integrations", {})
        
        for provider_slug, integration_data in integrations.items():
            if integration_data.get("enabled", False):
                print(f"\n   📊 Fetching data from {integration_data.get('provider_name', provider_slug)}...")
                
                data_result = await service.fetch_abandoned_cart_data(agent_id, provider_slug)
                
                if data_result["success"]:
                    data = data_result["data"]
                    print(f"   ✅ Mock data generated:")
                    print(f"      Platform: {data['platform']}")
                    print(f"      Abandoned carts: {data['total_abandoned_carts']}")
                    print(f"      Recovery value: ${data['total_recovery_value']:.2f}")
                    
                    # Show sample cart
                    if data.get("abandoned_carts"):
                        sample_cart = data["abandoned_carts"][0]
                        customer = sample_cart["customer"]
                        print(f"      Sample cart: {customer['first_name']} {customer['last_name']} - ${sample_cart['total_value']:.2f}")
                else:
                    print(f"   ❌ Failed to fetch data: {data_result['message']}")
        
        # Step 4: Create complete payload
        print(f"\n📦 Step 4: Creating complete payload for agent '{agent_name}'...")
        
        payload_result = await service.create_abandoned_cart_payload(agent_id)
        
        if payload_result["success"]:
            payload = payload_result["payload"]
            summary = payload["summary"]
            
            print(f"✅ Payload created successfully:")
            print(f"   Agent: {payload['agent']['name']}")
            print(f"   Company: {payload['company']['name']}")
            print(f"   Platforms: {summary['total_platforms']}")
            print(f"   Total abandoned carts: {summary['total_abandoned_carts']}")
            print(f"   Total recovery value: ${summary['total_recovery_value']:.2f}")
            print(f"   Currencies: {', '.join(summary['currencies'])}")
            
            # Step 5: Show payload structure (truncated)
            print(f"\n📄 Step 5: Payload structure preview...")
            print("   📋 Payload sections:")
            print(f"      • Agent info: {bool(payload.get('agent'))}")
            print(f"      • Company info: {bool(payload.get('company'))}")
            print(f"      • Voice config: {bool(payload.get('voice_config'))}")
            print(f"      • Platform data: {list(payload.get('platforms', {}).keys())}")
            print(f"      • Summary: {bool(payload.get('summary'))}")
            print(f"      • Metadata: {bool(payload.get('metadata'))}")
            
            # Show detailed platform data
            print(f"\n   🔗 Platform data details:")
            for platform, platform_data in payload.get("platforms", {}).items():
                print(f"      {platform}:")
                print(f"         • Abandoned carts: {platform_data.get('total_abandoned_carts', 0)}")
                print(f"         • Recovery value: ${platform_data.get('total_recovery_value', 0):.2f}")
                print(f"         • Generated at: {platform_data.get('generated_at')}")
            
            # Step 6: Simulate API call (mock endpoint)
            print(f"\n🚀 Step 6: Simulating external API call...")
            
            # Mock API endpoint for testing
            mock_api_url = "https://httpbin.org/post"  # Test endpoint that echoes back data
            
            try:
                api_result = await service.send_to_external_api(
                    payload=payload,
                    api_url=mock_api_url,
                    api_key="test-api-key-123"
                )
                
                if api_result["success"]:
                    print(f"✅ API call successful:")
                    print(f"   URL: {api_result['api_url']}")
                    print(f"   Status code: {api_result['status_code']}")
                    print(f"   Response size: {len(str(api_result['response_data']))} characters")
                else:
                    print(f"❌ API call failed: {api_result['message']}")
                
            except Exception as e:
                print(f"❌ API call error: {str(e)}")
        
        else:
            print(f"❌ Failed to create payload: {payload_result['message']}")
    
    print(f"\n" + "=" * 60)
    print("🎉 Abandoned cart system test completed!")


if __name__ == "__main__":
    asyncio.run(test_abandoned_cart_system())
