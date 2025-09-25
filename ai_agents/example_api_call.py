"""
Example API call for starting AI agent call
"""

import requests
import json


# Example API request to start AI agent call
def test_legacy_call():
    """Test legacy API format (backward compatibility)"""
    url = "http://localhost:5000/start-call"

    payload = {
        "phone_number": "+31687611451",  # Replace with actual number
        "customer_name": "John Doe",
        "customer_type": "vip",  # regular, new, vip
        "cart_id": "ORD-12345",
        "business_info": {
            "company_name": "TechCorp Solutions",
            "description": "Leading technology solutions provider",
            "website": "https://techcorp.com",
        },
        "agent_name": "Sarah AI Assistant",
        "tts_provider": "elevenlabs",  # elevenlabs or twilio
        "language": "en-US",
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.7},
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

    except Exception as e:
        print(f"Error: {e}")


def test_backend_payload():
    """Test backend abandoned cart payload format"""
    url = "http://localhost:5000/start-call"

    payload = {
        "agent": {
            "id": "agent_001",
            "name": "Sarah AI Assistant",
            "type": "abandoned_cart_recovery",
            "template_slug": "abandoned_cart_recovery_v2",
            "tts_provider": "elevenlabs",
            "language": "en-US",
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.7},
        },
        "business": {
            "name": "TechCorp Solutions",
            "description": "Leading technology solutions provider",
            "website": "https://techcorp.com",
            "industry": "technology",
        },
        "customer": {
            "phone": "+31687611451",  # Replace with actual number
            "name": "John Doe",
            "type": "abandoned_cart",
            "email": "john.doe@example.com",
        },
        "abandoned_carts": [
            {
                "cart_id": "cart_12345",
                "customer_phone": "+31687611451",
                "customer_name": "John Doe",
                "customer_email": "john.doe@example.com",
                "total_value": 259.99,
                "currency": "USD",
                "abandoned_at": "2025-09-22T10:30:00Z",
                "items": [
                    {
                        "product_id": "prod_001",
                        "name": "Premium Headphones",
                        "price": 199.99,
                        "quantity": 1,
                    },
                    {
                        "product_id": "prod_002",
                        "name": "Phone Case",
                        "price": 29.99,
                        "quantity": 2,
                    },
                ],
            }
        ],
        "platform_data": {
            "shopify": {"store_name": "techcorp-store", "abandoned_carts": []}
        },
        "summary": {
            "total_carts": 1,
            "total_value": 259.99,
            "recovery_potential": "high",
        },
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

    except Exception as e:
        print(f"Error: {e}")


def test_start_call():
    """Main test function - now tests both formats"""
    print("🧪 Testing Voice Agent API")
    print("1. Test Legacy Format (backward compatibility)")
    print("2. Test Backend Payload Format (new thread-based)")
    print("3. Test Both")

    choice = input("Your choice (1-3): ").strip()

    if choice == "1":
        print("\n📞 Testing Legacy Format...")
        test_legacy_call()
    elif choice == "2":
        print("\n📦 Testing Backend Payload Format...")
        test_backend_payload()
    elif choice == "3":
        print("\n📞 Testing Legacy Format...")
        test_legacy_call()
        print("\n📦 Testing Backend Payload Format...")
        test_backend_payload()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    print("🚀 Testing AI Agent Call Start")
    test_start_call()
