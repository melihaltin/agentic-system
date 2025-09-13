#!/usr/bin/env python3

import requests
import json
import time

# Test business registration
def test_business_registration():
    url = "http://localhost:8000/auth/supabase/register"
    
    # Use current timestamp to ensure unique email
    timestamp = int(time.time())
    payload = {
        "email": f"test{timestamp}@example.com",
        "password": "password123",
        "business_name": f"Test Business {timestamp}",
        "business_type": "retail",
        "business_website": f"https://testbusiness{timestamp}.com",
        "business_phone_number": f"+9055512345{timestamp % 100:02d}"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing business registration...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("FAILED!")
            try:
                print(f"Error Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Error Response (text): {response.text}")
                
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_business_registration()