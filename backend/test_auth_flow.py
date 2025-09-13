#!/usr/bin/env python3

import requests
import json
import uuid

# Test business registration
def test_business_registration():
    url = "http://localhost:8000/auth/supabase/register"
    
    # Use a unique email for each test
    unique_email = f"test_{str(uuid.uuid4())[:8]}@example.com"
    
    payload = {
        "email": unique_email,
        "password": "password123",
        "business_name": "Test Business",
        "business_type": "retail",
        "business_website": "https://testbusiness.com",
        "business_phone_number": "+905551234567"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing business registration...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
        else:
            print("FAILED!")
            try:
                print(f"Error Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Error Response (text): {response.text}")
            return None
                
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None

def test_business_login(email, password):
    url = "http://localhost:8000/auth/supabase/login"
    
    payload = {
        "email": email,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("\nTesting business login...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("LOGIN SUCCESS!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("LOGIN FAILED!")
            try:
                print(f"Error Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Error Response (text): {response.text}")
                
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    # Test registration
    registration_result = test_business_registration()
    
    # Test login if registration was successful
    if registration_result:
        test_business_login(registration_result.get("business", {}).get("email"), "password123")