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

    print("🤖 Twilio AI Voice Agent")
    print("1. Start with ElevenLabs TTS")
    print("2. Start with Twilio TTS")
    print("3. Make test call")
    print("4. Test ElevenLabs TTS (type text to convert to speech)")
    print("5. Start API Server (for dynamic call requests)")

    choice = input("Your choice (1-5): ").strip()

    if choice == "1":
        if not os.getenv("ELEVENLABS_API_KEY"):
            print("❌ ELEVENLABS_API_KEY is required for ElevenLabs TTS")
            exit(1)

        print("🚀 Starting server with ElevenLabs TTS...")
        voice_service = VoiceConfig.create_elevenlabs_config()
        app = create_webhook_server(voice_service)
        app.run(host="0.0.0.0", port=5000, debug=False)

    elif choice == "2":
        print("🚀 Starting server with Twilio TTS...")
        voice_service = VoiceConfig.create_twilio_config()
        app = create_webhook_server(voice_service)
        app.run(host="0.0.0.0", port=5000, debug=False)

    elif choice == "3":
        print("Choose TTS provider for test call:")
        print("1. ElevenLabs")
        print("2. Twilio")
        tts_choice = input("TTS choice (1-2): ").strip()

        if tts_choice == "1":
            if not os.getenv("ELEVENLABS_API_KEY"):
                print("❌ ELEVENLABS_API_KEY is required")
                exit(1)
            voice_service = VoiceConfig.create_elevenlabs_config()
        else:
            voice_service = VoiceConfig.create_twilio_config()

        agent = AbandonedCartAgent(voice_service)
        test_phone = input("Enter phone number (+1xxxxxxxxxx): ").strip()
        if test_phone:
            agent.make_outbound_call(test_phone)
        else:
            print("❌ Invalid phone number.")

    elif choice == "4":
        if not os.getenv("ELEVENLABS_API_KEY"):
            print("❌ ELEVENLABS_API_KEY is required for ElevenLabs TTS testing")
            exit(1)

        print("🎤 ElevenLabs TTS Test Mode")
        print("Type sentences to convert to speech. Type 'quit' to exit.")

        # Create ElevenLabs TTS service
        from services.tts.elevenlabs import ElevenLabsTTS
        from services.audio_storage import LocalAudioStorage

        tts = ElevenLabsTTS(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        )

        # Create audio storage for saving files
        storage = LocalAudioStorage(
            base_url="http://localhost:5000",  # Local server for audio files
            storage_path=os.getenv("AUDIO_STORAGE_PATH", "/tmp/audio"),
        )

        while True:
            text = input(
                "\n💬 Enter text to convert to speech (or 'quit' to exit): "
            ).strip()

            if text.lower() == "quit":
                print("👋 Goodbye!")
                break

            if not text:
                print("⚠️ Please enter some text!")
                continue

            try:
                print(f"🔊 Converting text to speech: '{text}'")

                # Generate audio and save to file
                audio_data = tts.generate_speech(text)
                audio_url = storage.save_audio(audio_data)

                print("✅ Audio generated successfully!")
                print(f"🎵 Audio saved to: {audio_url}")
                print(f"📂 Local file path: {storage.storage_path}")

                # Show audio file info
                audio_size = len(audio_data)
                print(f"📊 Audio size: {audio_size} bytes ({audio_size/1024:.1f} KB)")

            except Exception as e:
                print(f"❌ Error generating audio: {str(e)}")

    elif choice == "5":
        print("🌐 Starting API Server for dynamic call requests...")
        print("📡 Server will accept POST requests at /start-call endpoint")
        print("📋 Use example_api_call.py to test the API")

        # Create default voice service (will be overridden dynamically)
        voice_service = VoiceConfig.create_twilio_config()
        app = create_webhook_server(voice_service)

        print("🚀 API Server starting on http://localhost:5000")
        print("📞 Webhook endpoints:")
        print("   - POST /start-call (dynamic AI agent calls)")
        print("   - POST /webhook/outbound/start (Twilio webhook)")
        print("   - POST /webhook/outbound/process (Twilio webhook)")
        print("   - GET /health (health check)")

        app.run(host="0.0.0.0", port=5000, debug=False)

    else:
        print("❌ Invalid choice.")


if __name__ == "__main__":
    main()
