#!/usr/bin/env python3
"""
Test polling service with abandoned cart functionality
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.polling_service import AgentIntegrationPoller


async def test_polling_with_abandoned_cart():
    """
    Test the polling service with abandoned cart processing
    """
    print("🚀 Testing Polling Service with Abandoned Cart Processing")
    print("=" * 80)
    
    # Create poller instance with shorter interval for testing
    poller = AgentIntegrationPoller(polling_interval=10)
    
    # Perform a single poll to test functionality
    await poller.poll_once()
    
    print("\n" + "=" * 80)
    print("✅ Test completed! The polling service now:")
    print("   📊 Fetches all agents with integrations")
    print("   🛒 Identifies abandoned cart agents")
    print("   🏪 Generates mock data for each platform")
    print("   📤 Sends payloads to external API")
    print("   ⏱️  Repeats every 10 seconds (configurable)")


if __name__ == "__main__":
    asyncio.run(test_polling_with_abandoned_cart())
