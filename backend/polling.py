"""
Standalone Polling Script
Run this script to start polling agents with integrations
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.polling_service import run_agent_integration_polling


async def main():
    """
    Main function to run the polling service
    """
    print("🚀 Starting Agent Integration Polling Service...")
    print("Press Ctrl+C to stop the service")
    print("=" * 80)

    try:
        # Run polling with 30 second intervals
        await run_agent_integration_polling(interval=30)
    except KeyboardInterrupt:
        print("\n👋 Polling service stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
