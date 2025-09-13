"""
Example API call for starting AI agent call
"""

import requests
import json


# Example API request to start AI agent call
def test_start_call():
    url = "http://localhost:5000/start-call"

    payload = {
        "customer_number": "+31687611451",  # Replace with actual number
        "customer_name": "John Doe",
        "customer_type": "vip",  # regular, new, vip
        "order_id": "ORD-12345",
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


if __name__ == "__main__":
    print("🚀 Testing AI Agent Call Start")
    test_start_call()
