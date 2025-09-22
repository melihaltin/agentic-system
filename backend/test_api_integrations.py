"""
Integration API Test Script
Test integration APIs via HTTP requests
"""

import asyncio
import httpx
import json
import sys


async def test_integration_apis():
    """Test integration APIs"""

    base_url = "http://127.0.0.1:8001"

    print("🚀 Testing Integration APIs")
    print("=" * 50)

    async with httpx.AsyncClient() as client:

        # Test 1: Get available providers
        print("\n📦 Test 1: Get available providers")
        try:
            response = await client.get(f"{base_url}/integrations/providers")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Available providers: {', '.join(data['providers'])}")
                print(f"   Total: {data['total_providers']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

        # Test 2: Initialize integrations
        print("\n🔧 Test 2: Initialize integrations")
        try:
            response = await client.post(f"{base_url}/integrations/initialize")
            if response.status_code == 200:
                data = response.json()
                print(
                    f"✅ Initialized: {data['total_integrations']} integrations for {data['total_agents']} agents"
                )
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

        # Test 3: Get integrations status
        print("\n📊 Test 3: Get integrations status")
        try:
            response = await client.get(f"{base_url}/integrations/status")
            if response.status_code == 200:
                data = response.json()
                summary = data["summary"]
                print(f"✅ Active integrations: {summary['total_active']}")

                if summary["integrations"]:
                    integration = summary["integrations"][0]  # Get first integration
                    agent_id = integration["agent_id"]
                    provider_slug = integration["provider_slug"]

                    print(
                        f"   Sample: {integration['provider_name']} for agent {agent_id[:8]}..."
                    )

                    # Test 4: Test specific integration connection
                    print(
                        f"\n🧪 Test 4: Test connection for {integration['provider_name']}"
                    )
                    try:
                        test_response = await client.post(
                            f"{base_url}/integrations/test/{agent_id}/{provider_slug}"
                        )
                        if test_response.status_code == 200:
                            test_data = test_response.json()
                            conn_result = test_data["connection_result"]
                            if conn_result["success"]:
                                print(
                                    f"✅ Connection test passed ({conn_result['response_time']:.2f}s)"
                                )
                            else:
                                print(
                                    f"❌ Connection failed: {conn_result.get('error_message', 'Unknown error')}"
                                )
                        else:
                            print(
                                f"❌ Test failed: {test_response.status_code} - {test_response.text}"
                            )
                    except Exception as e:
                        print(f"❌ Error: {str(e)}")

                    # Test 5: Get integration status
                    print(
                        f"\n📋 Test 5: Get detailed status for {integration['provider_name']}"
                    )
                    try:
                        status_response = await client.get(
                            f"{base_url}/integrations/status/{agent_id}/{provider_slug}"
                        )
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data["status"]
                            print(
                                f"✅ Status: {status.get('connection_status', 'unknown')}"
                            )
                            print(
                                f"   Credentials valid: {'✅' if status_data['credentials_valid'] else '❌'}"
                            )
                            print(
                                f"   Supported events: {len(status_data['supported_events'])}"
                            )
                        else:
                            print(
                                f"❌ Status failed: {status_response.status_code} - {status_response.text}"
                            )
                    except Exception as e:
                        print(f"❌ Error: {str(e)}")

                    # Test 6: Try to fetch products (will likely fail due to invalid credentials)
                    print(
                        f"\n🛒 Test 6: Try to fetch products from {integration['provider_name']}"
                    )
                    try:
                        products_response = await client.get(
                            f"{base_url}/integrations/products/{agent_id}/{provider_slug}?limit=5"
                        )
                        if products_response.status_code == 200:
                            products_data = products_response.json()
                            if (
                                products_data["success"]
                                and products_data["result"]["success"]
                            ):
                                data = products_data["result"]["data"]
                                products = data.get("products", [])
                                print(f"✅ Products fetched: {len(products)} items")
                            else:
                                error_msg = products_data.get(
                                    "message", "Unknown error"
                                )
                                if products_data.get("result"):
                                    error_msg = products_data["result"].get(
                                        "error_message", error_msg
                                    )
                                print(f"❌ Products fetch failed: {error_msg}")
                        else:
                            print(
                                f"❌ Products request failed: {products_response.status_code} - {products_response.text}"
                            )
                    except Exception as e:
                        print(f"❌ Error: {str(e)}")
                else:
                    print("   No active integrations found")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 50)
    print("🎉 Integration API testing completed!")


if __name__ == "__main__":
    asyncio.run(test_integration_apis())
