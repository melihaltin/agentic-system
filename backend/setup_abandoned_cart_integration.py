#!/usr/bin/env python3
"""
Add integration to abandoned cart agent for testing
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.abandoned_cart_service import AbandonedCartAgentService


async def add_integration_to_abandoned_cart_agent():
    """
    Add Shopify integration to the abandoned cart agent for testing
    """
    print("🔧 Setting up integration for abandoned cart agent...")
    
    service = AbandonedCartAgentService()
    
    # Get abandoned cart agents
    agents = await service.get_abandoned_cart_agents()
    
    if not agents:
        print("❌ No abandoned cart agents found")
        return
    
    # Initialize integrations which will create mock integrations for testing
    integrations = await service.initialize_abandoned_cart_integrations()
    
    if integrations:
        print("✅ Mock integrations initialized")
        print(f"📊 Available integrations: {list(integrations.keys())}")
    else:
        print("❌ Failed to initialize integrations")


if __name__ == "__main__":
    asyncio.run(add_integration_to_abandoned_cart_agent())
