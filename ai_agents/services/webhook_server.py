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

    # Store active call configurations
    active_call_configs = {}

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

        # Get call information
        to_number = request.form.get("To")
        call_sid = request.form.get("CallSid")

        print(f"📱 Call started - To: {to_number}, SID: {call_sid}")

        response = VoiceResponse()
        gather = response.gather(
            input="speech",
            action="/webhook/outbound/process",
            method="POST",
            speech_timeout="auto",
            language="en-US",
        )

        # Find the correct agent for this call
        current_agent = agent
        current_voice_service = voice_service

        for call_config in active_call_configs.values():
            if call_config["config"].get("customer_number") == to_number:
                current_agent = call_config["agent"]
                current_voice_service = call_config["voice_service"]
                break

        # Generate dynamic welcome message using agent's first response
        welcome_text = current_agent.get_initial_greeting(to_number)

        if isinstance(current_voice_service.tts_provider, ElevenLabsTTS):
            try:
                audio_url = current_voice_service.text_to_speech(welcome_text)
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

        # Find the correct agent for this call
        current_agent = agent
        current_voice_service = voice_service

        for call_config in active_call_configs.values():
            if call_config["config"].get("customer_number") == to_number:
                current_agent = call_config["agent"]
                current_voice_service = call_config["voice_service"]
                break

        agent_response_text = current_agent.process_conversation(
            speech_result, to_number
        )

        # Check if conversation should end
        is_final = (
            "sms" in agent_response_text.lower()
            or "sending" in agent_response_text.lower()
            or "goodbye" in agent_response_text.lower()
        )

        if is_final:
            response = current_agent.generate_voice_response(
                agent_response_text, is_final=True
            )
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
            if isinstance(current_voice_service.tts_provider, ElevenLabsTTS):
                try:
                    audio_url = current_voice_service.text_to_speech(
                        agent_response_text
                    )
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

    @app.route("/start-call", methods=["POST"])
    def start_call_endpoint():
        """API endpoint to start AI agent call with custom configuration"""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ["customer_number", "business_info"]
            for field in required_fields:
                if not data.get(field):
                    return {"error": f"{field} is required"}, 400

            # Extract call configuration
            call_config = {
                "customer_number": data["customer_number"],
                "customer_name": data.get("customer_name", ""),
                "customer_type": data.get("customer_type", "regular"),
                "order_id": data.get("order_id", ""),
                "business_info": data["business_info"],
                "agent_name": data.get("agent_name", "AI Assistant"),
                "tts_provider": data.get(
                    "tts_provider", "elevenlabs"
                ),  # elevenlabs or twilio
                "language": data.get("language", "en-US"),
                "voice_settings": data.get("voice_settings", {}),
            }

            print(f"🚀 Starting AI agent call for: {call_config['customer_number']}")
            print(f"📋 Business: {call_config['business_info']['company_name']}")
            print(f"🎤 TTS Provider: {call_config['tts_provider']}")

            # Create dynamic voice service based on TTS provider
            from config.voice_config import VoiceConfig

            if call_config["tts_provider"].lower() == "elevenlabs":
                if not os.getenv("ELEVENLABS_API_KEY"):
                    return {"error": "ElevenLabs API key not configured"}, 500
                dynamic_voice_service = VoiceConfig.create_elevenlabs_config()
            else:
                dynamic_voice_service = VoiceConfig.create_twilio_config()

            # Create new agent instance with dynamic configuration
            dynamic_agent = TwilioOutboundAgent(dynamic_voice_service, call_config)

            # Start the call
            result = dynamic_agent.make_outbound_call(
                to_number=call_config["customer_number"],
                customer_name=call_config["customer_name"],
            )

            if result["success"]:
                # Store the configuration for this call
                call_sid = result["call_sid"]
                active_call_configs[call_sid] = {
                    "agent": dynamic_agent,
                    "config": call_config,
                    "voice_service": dynamic_voice_service,
                }

                return {
                    "success": True,
                    "call_sid": result["call_sid"],
                    "message": "AI agent call started successfully",
                    "config": {
                        "customer_number": call_config["customer_number"],
                        "business": call_config["business_info"]["company_name"],
                        "agent_name": call_config["agent_name"],
                        "tts_provider": call_config["tts_provider"],
                    },
                }
            else:
                return {"error": result["error"]}, 500

        except Exception as e:
            print(f"❌ Error starting call: {str(e)}")
            return {"error": f"Failed to start call: {str(e)}"}, 500

    @app.route("/make-call", methods=["POST"])
    def make_call_endpoint():
        """Legacy API endpoint for simple outbound calls"""
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
