"""
Abandoned Cart API Test Script
Test abandoned cart APIs via HTTP requests
"""
import asyncio
import httpx
import json


async def test_abandoned_cart_apis():
    """Test abandoned cart APIs"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🛒 Testing Abandoned Cart APIs")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Get abandoned cart agents
        print("\n📋 Test 1: Get abandoned cart agents")
        try:
            response = await client.get(f"{base_url}/abandoned-cart/agents")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['total_agents']} abandoned cart agents")
                
                agents = data.get('agents', [])
                for agent in agents:
                    agent_name = agent['agent_info'].get('custom_name', 'Unnamed')
                    company_name = agent.get('company_info', {}).get('company_name', 'Unknown')
                    print(f"   🤖 {agent_name} ({company_name})")
                
                # Store first agent for further testing
                test_agent_id = agents[0]['agent_id'] if agents else None
                
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                return
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return
        
        # Test 2: Initialize abandoned cart integrations
        print("\n🔧 Test 2: Initialize abandoned cart integrations")
        try:
            response = await client.post(f"{base_url}/abandoned-cart/initialize")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Initialized integrations for {data['total_agents']} agents")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        if test_agent_id:
            # Test 3: Generate mock data
            print("\n📊 Test 3: Generate mock abandoned cart data")
            try:
                response = await client.get(f"{base_url}/abandoned-cart/mock-data/shopify?company_name=Test Company")
                if response.status_code == 200:
                    data = response.json()
                    mock_data = data['data']
                    print(f"✅ Generated mock data:")
                    print(f"   Platform: {mock_data['platform']}")
                    print(f"   Company: {mock_data['company']}")
                    print(f"   Abandoned carts: {mock_data['total_abandoned_carts']}")
                    print(f"   Recovery value: ${mock_data['total_recovery_value']:.2f}")
                    
                    if mock_data.get('abandoned_carts'):
                        sample_cart = mock_data['abandoned_carts'][0]
                        customer = sample_cart['customer']
                        print(f"   Sample customer: {customer['first_name']} {customer['last_name']} - {customer['email']}")
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            # Test 4: Create payload for agent
            print(f"\n📦 Test 4: Create payload for agent")
            try:
                response = await client.get(f"{base_url}/abandoned-cart/payload/{test_agent_id}")
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        payload = data['payload']
                        summary = payload['summary']
                        print(f"✅ Payload created:")
                        print(f"   Agent: {payload['agent']['name']}")
                        print(f"   Company: {payload['company']['name']}")
                        print(f"   Platforms: {summary['total_platforms']}")
                        print(f"   Abandoned carts: {summary['total_abandoned_carts']}")
                        print(f"   Recovery value: ${summary['total_recovery_value']:.2f}")
                    else:
                        print(f"❌ Payload creation failed: {data['message']}")
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            # Test 5: Send payload to external API
            print(f"\n🚀 Test 5: Send payload to external API")
            try:
                payload_request = {
                    "api_url": "https://httpbin.org/post",
                    "api_key": "test-api-key-123"
                }
                
                response = await client.post(
                    f"{base_url}/abandoned-cart/send/{test_agent_id}",
                    json=payload_request
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        api_response = data['api_response']
                        payload_summary = data.get('payload_summary', {})
                        
                        print(f"✅ Payload sent successfully:")
                        print(f"   API URL: {api_response['api_url']}")
                        print(f"   Status code: {api_response['status_code']}")
                        print(f"   Payload summary:")
                        print(f"     • Platforms: {payload_summary.get('total_platforms', 0)}")
                        print(f"     • Abandoned carts: {payload_summary.get('total_abandoned_carts', 0)}")
                        print(f"     • Recovery value: ${payload_summary.get('total_recovery_value', 0):.2f}")
                    else:
                        print(f"❌ Send failed: {data['message']}")
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        # Test 6: Process all abandoned cart agents
        print(f"\n🔄 Test 6: Process all abandoned cart agents")
        try:
            response = await client.post(f"{base_url}/abandoned-cart/process-all")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Processed {data['total_processed']} agents:")
                print(f"   Successful: {data['successful']}")
                print(f"   Failed: {data['failed']}")
                
                for result in data['results']:
                    status = "✅" if result['success'] else "❌"
                    print(f"   {status} {result['agent_name']} ({result['company_name']})")
                    if result.get('payload_summary'):
                        summary = result['payload_summary']
                        print(f"       Carts: {summary.get('total_abandoned_carts', 0)}, Value: ${summary.get('total_recovery_value', 0):.2f}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Abandoned cart API testing completed!")


if __name__ == "__main__":
    asyncio.run(test_abandoned_cart_apis())
