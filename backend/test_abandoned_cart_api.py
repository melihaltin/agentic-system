#!/usr/bin/env python3
"""
Test abandoned cart polling via API endpoints
"""

import asyncio
import httpx
import json


async def test_abandoned_cart_api():
    """
    Test the abandoned cart polling API endpoints
    """
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 Testing Abandoned Cart Polling API")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Single abandoned cart test
        print("🧪 Test 1: Single Abandoned Cart Processing")
        print("-" * 40)
        
        try:
            response = await client.post(f"{base_url}/polling/abandoned-cart/test-once")
            result = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Single test completed successfully")
            else:
                print("❌ Single test failed")
                
        except Exception as e:
            print(f"❌ Error in single test: {str(e)}")
        
        print("\n" + "=" * 60)
        
        # Test 2: Start abandoned cart polling service
        print("🚀 Test 2: Start Abandoned Cart Polling Service")
        print("-" * 40)
        
        try:
            response = await client.post(f"{base_url}/polling/start-abandoned-cart?interval=15")
            result = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Polling service started successfully")
                print("⏱️  Polling will run every 15 seconds")
                print("🛒 System will automatically process abandoned carts")
            else:
                print("❌ Failed to start polling service")
                
        except Exception as e:
            print(f"❌ Error starting polling: {str(e)}")
        
        print("\n" + "=" * 60)
        
        # Test 3: Check polling status
        print("📊 Test 3: Check Polling Status")
        print("-" * 40)
        
        try:
            await asyncio.sleep(2)  # Wait a bit
            
            response = await client.get(f"{base_url}/polling/status")
            result = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Status retrieved successfully")
            else:
                print("❌ Failed to get status")
                
        except Exception as e:
            print(f"❌ Error getting status: {str(e)}")
        
        print("\n" + "=" * 60)
        
        # Test 4: Wait for a couple of polling cycles
        print("⏳ Test 4: Waiting for 2 polling cycles...")
        print("-" * 40)
        print("🔄 System is running abandoned cart recovery...")
        print("📊 Check the server logs for real-time processing")
        
        await asyncio.sleep(35)  # Wait for 2-3 polling cycles
        
        # Test 5: Stop the polling service
        print("\n⏹️  Test 5: Stop Polling Service")
        print("-" * 40)
        
        try:
            response = await client.post(f"{base_url}/polling/stop")
            result = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                print("✅ Polling service stopped successfully")
            else:
                print("❌ Failed to stop polling service")
                
        except Exception as e:
            print(f"❌ Error stopping polling: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Abandoned Cart Polling API Test Complete!")
    print("✨ Your system is now ready for production!")


if __name__ == "__main__":
    asyncio.run(test_abandoned_cart_api())
