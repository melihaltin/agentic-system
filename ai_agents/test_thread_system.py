"""
Test Script for Thread-Based Voice Agent System
Tests concurrent payload processing and thread management
"""

import requests
import json
import time
import threading
from typing import Dict, Any, List


class ThreadBasedVoiceAgentTester:
    """Test class for thread-based voice agent system"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []

    def test_health_check(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Thread system: {data.get('thread_system', 'unknown')}")
                print(f"   Active threads: {data.get('active_threads', 0)}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False

    def create_test_payload(self, customer_id: int) -> Dict[str, Any]:
        """Create test payload for abandoned cart scenario"""
        return {
            "agent": {
                "id": f"agent_test_{customer_id}",
                "name": f"Sarah Assistant {customer_id}",
                "type": "abandoned_cart_recovery",
                "template_slug": "abandoned_cart_recovery_v2",
                "tts_provider": "elevenlabs",
                "language": "en-US",
                "voice_settings": {"stability": 0.6, "similarity_boost": 0.7},
            },
            "business": {
                "name": f"Test Store {customer_id}",
                "description": f"Test e-commerce store {customer_id}",
                "website": f"https://teststore{customer_id}.com",
                "industry": "retail",
            },
            "customer": {
                "phone": f"+155512300{customer_id:02d}",  # Fake numbers for testing
                "name": f"Test Customer {customer_id}",
                "type": "abandoned_cart",
                "email": f"customer{customer_id}@test.com",
            },
            "abandoned_carts": [
                {
                    "cart_id": f"cart_{customer_id}_{int(time.time())}",
                    "customer_phone": f"+155512300{customer_id:02d}",
                    "customer_name": f"Test Customer {customer_id}",
                    "customer_email": f"customer{customer_id}@test.com",
                    "total_value": 99.99 + (customer_id * 10),
                    "currency": "USD",
                    "abandoned_at": "2025-09-22T10:30:00Z",
                    "items": [
                        {
                            "product_id": f"prod_{customer_id}_1",
                            "name": f"Test Product {customer_id}",
                            "price": 49.99 + (customer_id * 5),
                            "quantity": 1,
                        }
                    ],
                }
            ],
            "platform_data": {
                "shopify": {
                    "store_name": f"teststore{customer_id}",
                    "abandoned_carts": [],
                }
            },
            "summary": {
                "total_carts": 1,
                "total_value": 99.99 + (customer_id * 10),
                "recovery_potential": "high",
            },
        }

    def create_legacy_payload(self, customer_id: int) -> Dict[str, Any]:
        """Create legacy format payload"""
        return {
            "phone_number": f"+155512400{customer_id:02d}",
            "customer_name": f"Legacy Customer {customer_id}",
            "customer_type": "regular",
            "business_info": {
                "company_name": f"Legacy Business {customer_id}",
                "description": f"Legacy test business {customer_id}",
                "website": f"https://legacy{customer_id}.com",
            },
            "agent_name": f"Legacy Agent {customer_id}",
            "tts_provider": "twilio",
            "language": "en-US",
        }

    def send_test_payload(
        self, payload: Dict[str, Any], test_name: str
    ) -> Dict[str, Any]:
        """Send test payload and return response"""
        try:
            print(f"📤 Sending {test_name}...")

            response = requests.post(
                f"{self.base_url}/start-call",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            result = {
                "test_name": test_name,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else response.text
                ),
                "timestamp": time.time(),
            }

            if result["success"]:
                print(f"✅ {test_name} successful")
                if "thread_id" in result["response"]:
                    print(f"   Thread ID: {result['response']['thread_id']}")
                if "customer_phone" in result["response"]:
                    print(f"   Customer: {result['response']['customer_phone']}")
            else:
                print(f"❌ {test_name} failed: {result['response']}")

            return result

        except Exception as e:
            result = {
                "test_name": test_name,
                "status_code": None,
                "success": False,
                "response": str(e),
                "timestamp": time.time(),
            }
            print(f"❌ {test_name} error: {str(e)}")
            return result

    def get_threads_status(self) -> Dict[str, Any]:
        """Get current threads status"""
        try:
            response = requests.get(f"{self.base_url}/threads", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def test_concurrent_payloads(self, num_payloads: int = 3):
        """Test concurrent payload processing"""
        print(f"\n🧪 Testing {num_payloads} concurrent payloads...")

        # Create test payloads
        payloads = []
        for i in range(num_payloads):
            if i % 2 == 0:
                payload = self.create_test_payload(i + 1)
                test_name = f"Backend Payload {i + 1}"
            else:
                payload = self.create_legacy_payload(i + 1)
                test_name = f"Legacy Payload {i + 1}"

            payloads.append((payload, test_name))

        # Send payloads concurrently
        results = []
        threads = []

        def send_payload(payload_data, test_name):
            result = self.send_test_payload(payload_data, test_name)
            results.append(result)

        # Start all threads
        for payload, test_name in payloads:
            thread = threading.Thread(target=send_payload, args=(payload, test_name))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        print(f"\n📊 Concurrent test results:")
        print(f"   Successful: {len(successful)}/{num_payloads}")
        print(f"   Failed: {len(failed)}/{num_payloads}")

        if failed:
            print(f"   Failed tests:")
            for result in failed:
                print(f"     - {result['test_name']}: {result['response']}")

        return results

    def test_thread_monitoring(self, duration: int = 10):
        """Test thread monitoring for specified duration"""
        print(f"\n📊 Monitoring threads for {duration} seconds...")

        start_time = time.time()
        while time.time() - start_time < duration:
            status = self.get_threads_status()

            if "error" not in status:
                print(f"   Active threads: {status['total_threads']}")
                if status["status_summary"]:
                    summary = ", ".join(
                        [f"{k}: {v}" for k, v in status["status_summary"].items()]
                    )
                    print(f"   Status: {summary}")
            else:
                print(f"   Error getting status: {status['error']}")

            time.sleep(2)

        print("✅ Thread monitoring completed")

    def run_complete_test_suite(self):
        """Run complete test suite"""
        print("🚀 Starting Thread-Based Voice Agent Test Suite")
        print("=" * 60)

        # Test 1: Health check
        print("\n1️⃣ Testing Health Check...")
        if not self.test_health_check():
            print("❌ Health check failed. Make sure server is running.")
            return

        # Test 2: Single payload
        print("\n2️⃣ Testing Single Backend Payload...")
        single_payload = self.create_test_payload(999)
        self.send_test_payload(single_payload, "Single Backend Payload")

        # Test 3: Single legacy payload
        print("\n3️⃣ Testing Single Legacy Payload...")
        legacy_payload = self.create_legacy_payload(998)
        self.send_test_payload(legacy_payload, "Single Legacy Payload")

        # Test 4: Concurrent payloads
        print("\n4️⃣ Testing Concurrent Payloads...")
        self.test_concurrent_payloads(5)

        # Test 5: Monitor threads
        print("\n5️⃣ Monitoring Active Threads...")
        self.test_thread_monitoring(15)

        # Final status
        print("\n6️⃣ Final Thread Status...")
        final_status = self.get_threads_status()
        if "error" not in final_status:
            print(f"   Total threads: {final_status['total_threads']}")
            for thread in final_status.get("threads", []):
                print(
                    f"   - {thread['thread_id']}: {thread['status']} ({thread['customer_name']})"
                )

        print("\n✅ Test suite completed!")
        print("=" * 60)


def main():
    """Main test function"""
    print("🧪 Thread-Based Voice Agent System Tester")
    print("Make sure the API server is running on localhost:5000")
    print()

    tester = ThreadBasedVoiceAgentTester()

    print("Select test to run:")
    print("1. Complete test suite")
    print("2. Health check only")
    print("3. Single backend payload")
    print("4. Single legacy payload")
    print("5. Concurrent payloads test")
    print("6. Thread monitoring only")

    choice = input("Your choice (1-6): ").strip()

    if choice == "1":
        tester.run_complete_test_suite()
    elif choice == "2":
        tester.test_health_check()
    elif choice == "3":
        payload = tester.create_test_payload(1)
        tester.send_test_payload(payload, "Single Backend Payload Test")
    elif choice == "4":
        payload = tester.create_legacy_payload(1)
        tester.send_test_payload(payload, "Single Legacy Payload Test")
    elif choice == "5":
        num_payloads = int(input("Number of concurrent payloads (default 3): ") or "3")
        tester.test_concurrent_payloads(num_payloads)
    elif choice == "6":
        duration = int(input("Monitoring duration in seconds (default 10): ") or "10")
        tester.test_thread_monitoring(duration)
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
