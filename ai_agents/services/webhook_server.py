"""
Flask webhook server for Twilio voice integration
"""

import os
from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse

from agents.voice.agent import TwilioOutboundAgent
from services.voice_service import VoiceService
from services.tts.elevenlabs import ElevenLabsTTS


def create_webhook_server(voice_service: VoiceService) -> Flask:
    """Create Flask server for Twilio webhooks."""
    app = Flask(__name__)
    agent = TwilioOutboundAgent(voice_service)

    # Serve audio files for ElevenLabs
    @app.route("/audio/<filename>")
    def serve_audio(filename):
        """Serve audio files"""
        audio_path = os.getenv("AUDIO_STORAGE_PATH", "/tmp/audio")
        return send_from_directory(audio_path, filename)

    @app.route("/webhook/outbound/start", methods=["POST"])
    def handle_outbound_start():
        """Triggered when outbound call starts"""
        print("📞 Incoming Webhook request: /webhook/outbound/start")

        response = VoiceResponse()
        gather = response.gather(
            input="speech",
            action="/webhook/outbound/process",
            method="POST",
            speech_timeout="auto",
            language="en-US",
        )

        # Use the voice service for TTS
        welcome_text = (
            "Hello, I am calling to offer you a special promo code. Are you interested?"
        )

        if isinstance(voice_service.tts_provider, ElevenLabsTTS):
            try:
                audio_url = voice_service.text_to_speech(welcome_text)
                gather.play(audio_url)
            except Exception as e:
                print(f"❌ ElevenLabs error, using Twilio TTS: {e}")
                gather.say(welcome_text, voice="Polly.Joanna", language="en-US")
        else:
            gather.say(welcome_text, voice="Polly.Joanna", language="en-US")

        response.say(
            "I didn't get a response. Have a great day.",
            voice="Polly.Joanna",
            language="en-US",
        )
        response.hangup()

        return str(response)

    @app.route("/webhook/outbound/process", methods=["POST"])
    def handle_outbound_process():
        """Process user speech input."""
        to_number = request.form.get("To")
        speech_result = request.form.get("SpeechResult", "")

        print(f"🎤 User response ({to_number}): '{speech_result}'")

        agent_response_text = agent.process_conversation(speech_result, to_number)

        # Check if conversation should end
        is_final = (
            "sms" in agent_response_text.lower()
            or "sending" in agent_response_text.lower()
            or "goodbye" in agent_response_text.lower()
        )

        if is_final:
            response = agent.generate_voice_response(agent_response_text, is_final=True)
        else:
            response = VoiceResponse()
            gather = response.gather(
                input="speech",
                action="/webhook/outbound/process",
                method="POST",
                speech_timeout="auto",
                language="en-US",
            )

            # Generate voice response using the configured TTS
            if isinstance(voice_service.tts_provider, ElevenLabsTTS):
                try:
                    audio_url = voice_service.text_to_speech(agent_response_text)
                    gather.play(audio_url)
                except Exception as e:
                    print(f"❌ ElevenLabs error, using Twilio TTS: {e}")
                    gather.say(
                        agent_response_text, voice="Polly.Joanna", language="en-US"
                    )
            else:
                gather.say(agent_response_text, voice="Polly.Joanna", language="en-US")

            response.say(
                "I didn't get your response. Goodbye.",
                voice="Polly.Joanna",
                language="en-US",
            )
            response.hangup()

        return str(response)

    @app.route("/make-call", methods=["POST"])
    def make_call_endpoint():
        """API endpoint to make outbound calls"""
        data = request.get_json()
        phone_number = data.get("phone_number")
        if not phone_number:
            return {"error": "phone_number is required"}, 400
        result = agent.make_outbound_call(phone_number)
        return result

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "tts_provider": type(voice_service.tts_provider).__name__,
        }

    return app
