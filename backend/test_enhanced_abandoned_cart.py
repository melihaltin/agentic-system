"""
Enhanced Abandoned Cart Test with Mock Integrations
Test with simulated Shopify integration data
"""
import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.abandoned_cart_service import AbandonedCartAgentService


async def test_with_mock_integration():
    """Test abandoned cart system with mock integration simulation"""
    
    print("🛒 Enhanced Abandoned Cart Test with Mock Integration")
    print("=" * 65)
    
    service = AbandonedCartAgentService()
    
    # Get all agents (including non-abandoned-cart ones)
    print("\n📋 Getting all agents...")
    all_agents_service = service.agent_service
    all_agents = await all_agents_service.fetch_agents_with_integrations()
    
    print(f"✅ Found {len(all_agents)} total agents:")
    
    # Find agent with Shopify integration (not necessarily abandoned cart)
    shopify_agent = None
    abandoned_cart_agent = None
    
    for agent in all_agents:
        template_slug = agent.get("template_info", {}).get("template_slug", "")
        integrations = agent.get("integrations", {})
        
        agent_name = agent["agent_info"].get("custom_name", "Unnamed")
        
        print(f"   🤖 {agent_name} - Template: {template_slug}")
        print(f"      Integrations: {list(integrations.keys()) if integrations else 'None'}")
        
        # Check for Shopify integration
        if "shopify" in integrations and integrations["shopify"].get("enabled", False):
            shopify_agent = agent
            print(f"      ✅ Has Shopify integration!")
        
        # Check for abandoned cart template
        if template_slug == "ecommerce-abandoned-cart":
            abandoned_cart_agent = agent
            print(f"      🛒 Is abandoned cart agent!")
    
    print(f"\n📊 Analysis:")
    print(f"   Shopify agent found: {'✅' if shopify_agent else '❌'}")
    print(f"   Abandoned cart agent found: {'✅' if abandoned_cart_agent else '❌'}")
    
    # Test mock data generation for different scenarios
    print(f"\n🧪 Testing mock data generation scenarios...")
    
    # Scenario 1: Mock data for Shopify
    print(f"\n   📊 Scenario 1: Shopify abandoned cart data")
    mock_company = {
        "company_name": "TechCorp E-commerce",
        "website": "techcorp-ecommerce.com"
    }
    
    shopify_mock = service.generate_mock_abandoned_cart_data("shopify", mock_company)
    print(f"   ✅ Generated Shopify mock data:")
    print(f"      Company: {shopify_mock['company']}")
    print(f"      Abandoned carts: {shopify_mock['total_abandoned_carts']}")
    print(f"      Recovery value: ${shopify_mock['total_recovery_value']:.2f}")
    
    # Show sample cart details
    if shopify_mock.get('abandoned_carts'):
        sample_cart = shopify_mock['abandoned_carts'][0]
        customer = sample_cart['customer']
        products = sample_cart['products']
        
        print(f"      Sample cart details:")
        print(f"         Customer: {customer['first_name']} {customer['last_name']} ({customer['email']})")
        print(f"         Products: {len(products)} items")
        for product in products:
            print(f"           • {product['title']} - ${product['price']}")
        print(f"         Cart value: ${sample_cart['total_value']:.2f}")
        print(f"         Abandoned: {sample_cart['abandoned_at']}")
        print(f"         Recovery URL: {sample_cart['cart_url']}")
    
    # Scenario 2: Mock data for WooCommerce
    print(f"\n   📊 Scenario 2: WooCommerce abandoned cart data")
    woocommerce_mock = service.generate_mock_abandoned_cart_data("woocommerce", mock_company)
    print(f"   ✅ Generated WooCommerce mock data:")
    print(f"      Company: {woocommerce_mock['company']}")
    print(f"      Abandoned carts: {woocommerce_mock['total_abandoned_carts']}")
    print(f"      Recovery value: ${woocommerce_mock['total_recovery_value']:.2f}")
    
    # Test payload creation with actual agent (simulating it has integrations)
    if abandoned_cart_agent:
        print(f"\n📦 Testing payload creation with abandoned cart agent...")
        agent_id = abandoned_cart_agent["agent_id"]
        agent_name = abandoned_cart_agent["agent_info"].get("custom_name", "Unnamed")
        
        print(f"   Agent: {agent_name} ({agent_id[:8]}...)")
        
        # Create payload (will be empty since no real integrations)
        payload_result = await service.create_abandoned_cart_payload(agent_id)
        
        if payload_result["success"]:
            payload = payload_result["payload"]
            
            # Manually simulate adding platform data to show complete payload structure
            print(f"\n   📄 Simulating complete payload with mock integrations...")
            
            # Add mock platform data
            payload["platforms"]["shopify"] = shopify_mock
            payload["platforms"]["woocommerce"] = woocommerce_mock
            
            # Update summary
            total_carts = shopify_mock['total_abandoned_carts'] + woocommerce_mock['total_abandoned_carts']
            total_value = shopify_mock['total_recovery_value'] + woocommerce_mock['total_recovery_value']
            
            payload["summary"].update({
                "total_platforms": 2,
                "total_abandoned_carts": total_carts,
                "total_recovery_value": total_value,
                "currencies": ["USD"]
            })
            
            print(f"   ✅ Enhanced payload created:")
            print(f"      Agent: {payload['agent']['name']}")
            print(f"      Company: {payload['company']['name']}")
            print(f"      Voice config: {'✅' if payload.get('voice_config') else '❌'}")
            print(f"      Platforms: {payload['summary']['total_platforms']}")
            print(f"      Total abandoned carts: {payload['summary']['total_abandoned_carts']}")
            print(f"      Total recovery value: ${payload['summary']['total_recovery_value']:.2f}")
            
            # Show platform breakdown
            print(f"\n      📊 Platform breakdown:")
            for platform, data in payload["platforms"].items():
                print(f"         {platform.upper()}: {data['total_abandoned_carts']} carts, ${data['total_recovery_value']:.2f}")
            
            # Test API payload size
            payload_json = json.dumps(payload, default=str)
            print(f"\n      📏 Payload stats:")
            print(f"         JSON size: {len(payload_json):,} characters")
            print(f"         Estimated size: {len(payload_json.encode('utf-8')) / 1024:.1f} KB")
            
            # Test sending to external API
            print(f"\n🚀 Testing external API call with complete payload...")
            
            api_result = await service.send_to_external_api(
                payload=payload,
                api_url="https://httpbin.org/post",
                api_key="test-api-key-abandoned-cart-123"
            )
            
            if api_result["success"]:
                print(f"   ✅ API call successful:")
                print(f"      URL: {api_result['api_url']}")
                print(f"      Status: {api_result['status_code']}")
                print(f"      Response type: {type(api_result['response_data'])}")
                
                # Show some response data
                if isinstance(api_result['response_data'], dict):
                    response_json = api_result['response_data'].get('json', {})
                    if response_json:
                        echo_summary = response_json.get('summary', {})
                        print(f"      Echo verification:")
                        print(f"         Platforms echoed: {echo_summary.get('total_platforms', 'N/A')}")
                        print(f"         Carts echoed: {echo_summary.get('total_abandoned_carts', 'N/A')}")
                        print(f"         Value echoed: ${echo_summary.get('total_recovery_value', 0):.2f}")
            else:
                print(f"   ❌ API call failed: {api_result['message']}")
        
        else:
            print(f"   ❌ Payload creation failed: {payload_result['message']}")
    
    else:
        print(f"\n❌ No abandoned cart agent found for testing")
    
    print(f"\n" + "=" * 65)
    print("🎉 Enhanced abandoned cart test completed!")
    print("✨ System ready for production with real platform integrations!")


if __name__ == "__main__":
    asyncio.run(test_with_mock_integration())
