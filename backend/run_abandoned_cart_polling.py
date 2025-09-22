#!/usr/bin/env python3
"""
Test complete abandoned cart polling system with continuous operation
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.polling_service import AgentIntegrationPoller


async def test_continuous_abandoned_cart_polling():
    """
    Test continuous abandoned cart polling with real scenario
    """
    print("🚀 Starting Continuous Abandoned Cart Polling System")
    print("=" * 80)
    print("📋 This system will:")
    print("   • Poll every 10 seconds for abandoned cart agents")
    print("   • Generate mock abandoned cart data for each platform")
    print("   • Create payloads with company + customer + cart data")
    print("   • Send to external API endpoints")
    print("   • Show real-time recovery analytics")
    print("=" * 80)
    
    # Create poller with 10 second intervals for demo
    poller = AgentIntegrationPoller(polling_interval=10)
    
    print("⚡ Starting polling loop... (Press Ctrl+C to stop)")
    print("-" * 80)
    
    try:
        # Start the polling loop - this runs continuously
        await poller.start_polling()
    except KeyboardInterrupt:
        print("\n⏹️  Polling stopped by user")
        await poller.stop_polling()
        print("✅ System shutdown complete")


if __name__ == "__main__":
    # Run the continuous polling system
    asyncio.run(test_continuous_abandoned_cart_polling())
