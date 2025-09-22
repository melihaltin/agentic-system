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

    print("🤖 Twilio AI Voice Agent - Thread-Based System")
    print("1. Start with ElevenLabs TTS")
    print("2. Start with Twilio TTS")
    print("3. Make test call")
    print("4. Test ElevenLabs TTS (type text to convert to speech)")
    print("5. Start Thread-Based API Server (supports concurrent calls)")
    print("6. Monitor Active Threads")

    choice = input("Your choice (1-6): ").strip()

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
        print("🌐 Starting Thread-Based API Server...")
        print("🧵 Server supports concurrent customer interactions")
        print("📡 Accepts backend abandoned cart payloads and legacy API calls")
        print("📋 Use example_api_call.py to test the API")

        # Create default voice service (will be overridden dynamically)
        voice_service = VoiceConfig.create_twilio_config()
        app = create_webhook_server(voice_service)

        print("🚀 Thread-Based API Server starting on http://localhost:5000")
        print("📞 Available endpoints:")
        print("   - POST /start-call (backend payloads & legacy calls)")
        print("   - GET /threads (view all active threads)")
        print("   - GET /threads/<thread_id> (view specific thread)")
        print("   - POST /threads/<thread_id>/cancel (cancel thread)")
        print("   - POST /webhook/outbound/start (Twilio webhook)")
        print("   - POST /webhook/outbound/process (Twilio webhook)")
        print("   - GET /health (health check with thread stats)")
        print("")
        print("🎯 Thread System Features:")
        print("   - Concurrent customer interactions")
        print("   - Individual agent instances per thread")
        print("   - Real-time thread monitoring")
        print("   - Automatic cleanup")

        app.run(host="0.0.0.0", port=5000, debug=False)

    elif choice == "6":
        print("🔍 Thread Monitor")
        print("Monitor active voice agent threads in real-time")
        print("Note: This requires the API server to be running on localhost:5000")

        import requests
        import time
        import json

        def monitor_threads():
            try:
                while True:
                    response = requests.get("http://localhost:5000/threads", timeout=5)
                    if response.status_code == 200:
                        data = response.json()

                        print("\n" + "=" * 60)
                        print(f"📊 THREAD MONITOR - {time.strftime('%H:%M:%S')}")
                        print("=" * 60)
                        print(f"Total Active Threads: {data['total_threads']}")

                        if data["status_summary"]:
                            print("\nStatus Summary:")
                            for status, count in data["status_summary"].items():
                                print(f"  {status}: {count}")

                        if data["threads"]:
                            print("\nActive Threads:")
                            for thread in data["threads"]:
                                duration = ""
                                if thread["started_at"]:
                                    from datetime import datetime

                                    start_time = datetime.fromisoformat(
                                        thread["started_at"].replace("Z", "+00:00")
                                    )
                                    current_time = datetime.now(start_time.tzinfo)
                                    duration = str(current_time - start_time).split(
                                        "."
                                    )[0]

                                print(f"  🧵 {thread['thread_id']}")
                                print(
                                    f"     Customer: {thread['customer_name']} ({thread['customer_phone']})"
                                )
                                print(f"     Status: {thread['status']}")
                                print(f"     Duration: {duration}")
                                if thread["call_sid"]:
                                    print(f"     Call SID: {thread['call_sid']}")
                                if thread["conversation_length"] > 0:
                                    print(
                                        f"     Messages: {thread['conversation_length']}"
                                    )
                                print()
                        else:
                            print("\nNo active threads")

                    else:
                        print(
                            f"❌ Failed to connect to API server: {response.status_code}"
                        )
                        break

                    time.sleep(3)  # Update every 3 seconds

            except requests.exceptions.ConnectionError:
                print(
                    "❌ Cannot connect to API server. Make sure it's running on localhost:5000"
                )
            except KeyboardInterrupt:
                print("\n👋 Thread monitoring stopped")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

        monitor_threads()

    else:
        print("❌ Invalid choice.")


if __name__ == "__main__":
    main()
