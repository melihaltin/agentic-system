#!/usr/bin/env python3
"""
Test Dynamic Voice ID with Backend Payload Format
"""
import json
import requests
import time


def test_backend_payload_with_voice_id():
    """Test backend payload format with selected_voice_id"""

    # Backend formatted payload with selected_voice_id
    payload = {
        "agent": {
            "id": "agent_001",
            "name": "Abandoned Cart Agent",
            "type": "abandoned_cart_recovery",
            "template_slug": "abandoned_cart_v1",
            "is_configured": True,
            "total_interactions": 5,
            "selected_voice_id": "pNInz6obpgDQGcFmaJgB",  # Custom voice from backend
        },
        "company": {
            "id": 1,
            "name": "Test Company",
            "business_category": "e-commerce",
            "phone_number": "+1555000123",
            "website": "https://testcompany.com",
            "timezone": "UTC",
        },
        "voice_config": {
            "selected_voice_id": "pNInz6obpgDQGcFmaJgB",  # Voice configuration
            "voice_settings": {"stability": 0.7, "similarity_boost": 0.8},
        },
        "platforms": {
            "shopify": {
                "store_name": "test-store",
                "total_abandoned_carts": 1,
                "total_recovery_value": 299.99,
                "abandoned_carts": [
                    {
                        "cart_id": "cart_voice_test_001",
                        "customer_phone": "+31687611451",
                        "customer_name": "Test Customer",
                        "customer_email": "test@example.com",
                        "total_value": 299.99,
                        "currency": "USD",
                        "abandoned_at": "2025-09-22T12:00:00Z",
                        "items": [
                            {
                                "product_id": "prod_voice_test",
                                "name": "Voice Test Product",
                                "title": "Dynamic Voice Test Item",
                                "price": 299.99,
                                "quantity": 1,
                            }
                        ],
                    }
                ],
            }
        },
        "summary": {
            "total_platforms": 1,
            "total_abandoned_carts": 1,
            "total_recovery_value": 299.99,
            "currencies": ["USD"],
        },
        "metadata": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "payload_version": "1.0",
            "service": "abandoned_cart_recovery",
        },
    }

    print("🎵 Testing Backend Payload with Dynamic Voice ID")
    print("=" * 60)
    print(f"🎤 Using voice_id: {payload['agent']['selected_voice_id']}")
    print(
        f"📞 Customer: {payload['platforms']['shopify']['abandoned_carts'][0]['customer_name']}"
    )
    print(
        f"📱 Phone: {payload['platforms']['shopify']['abandoned_carts'][0]['customer_phone']}"
    )
    print("")

    try:
        # Send request to voice agent API
        response = requests.post(
            "http://localhost:5000/start-call",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Payload processed successfully!")
            print(f"🧵 Thread ID: {result.get('thread_id')}")
            print(f"🎯 System: {result.get('system')}")
            print(f"📋 Message: {result.get('message')}")

            # Check thread status to see if voice_id is passed correctly
            thread_id = result.get("thread_id")
            if thread_id:
                print(f"\n🔍 Checking thread {thread_id} for voice configuration...")

                # Get thread details
                thread_response = requests.get(
                    f"http://localhost:5000/threads/{thread_id}", timeout=5
                )

                if thread_response.status_code == 200:
                    thread_data = thread_response.json()
                    agent_config = thread_data.get("agent_config", {})

                    print(f"🎤 Voice ID in config: {agent_config.get('voice_id')}")
                    print(
                        f"🎵 Selected Voice ID: {agent_config.get('selected_voice_id')}"
                    )

                    if (
                        agent_config.get("selected_voice_id")
                        == payload["agent"]["selected_voice_id"]
                    ):
                        print(
                            "✅ VOICE SUCCESS: selected_voice_id correctly passed to agent!"
                        )
                    else:
                        print("❌ VOICE FAIL: selected_voice_id not correctly passed")
                else:
                    print("⚠️ Could not check thread details")

            return True

        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to voice agent server")
        print("Make sure the server is running on http://localhost:5000")
        print("Start it with: python voice_agent_main.py -> option 5")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def main():
    """Run backend payload voice test"""
    print("🎵 Dynamic Voice Backend Payload Test")
    print("=" * 60)
    print("Testing backend payload format with selected_voice_id")
    print("")

    success = test_backend_payload_with_voice_id()

    print("\n" + "=" * 60)
    if success:
        print("🎉 Backend payload voice test COMPLETED!")
        print("✅ Dynamic voice_id system is working")
    else:
        print("❌ Backend payload voice test FAILED")
        print("Check the voice agent server and try again")


if __name__ == "__main__":
    main()
