"""
Voice Agent Main Application
"""

import os
from dotenv import load_dotenv

from config.voice_config import VoiceConfig
from services.webhook_server import create_webhook_server
from agents.ecommerce.abandoned_cart_agent.agent import AbandonedCartAgent

load_dotenv()


def check_environment_variables():
    """Check required environment variables"""
    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "GOOGLE_API_KEY",
        "WEBHOOK_BASE_URL",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True


def main():
    """Main application entry point"""
    if not check_environment_variables():
        exit(1)

    voice_service = VoiceConfig.create_twilio_config()
    app = create_webhook_server(voice_service)

    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
