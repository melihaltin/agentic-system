"""
Flask webhook server for Twilio voice integration
Thread-based system supporting concurrent customer interactions
"""

import os
from flask import Flask, request, send_from_directory, jsonify
from twilio.twiml.voice_response import VoiceResponse

from agents.ecommerce.abandoned_cart_agent.agent import AbandonedCartAgent
from services.voice_service import VoiceService
from services.tts.elevenlabs import ElevenLabsTTS
from core.thread_manager import get_thread_manager, ThreadStatus


def create_webhook_server(voice_service: VoiceService) -> Flask:
    """Create Flask server for Twilio webhooks with thread support."""
    app = Flask(__name__)

    # Get thread manager instance
    thread_manager = get_thread_manager()

    # Legacy agent for backward compatibility
    agent = AbandonedCartAgent(voice_service)

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

        # Find thread context for this call
        thread_context = None

        # First try to find by call SID
        if call_sid:
            thread_context = thread_manager.get_thread_by_call_sid(call_sid)

        # If not found, try to find by phone number
        if not thread_context and to_number:
            thread_context = thread_manager.get_thread_by_phone(to_number)
            # Update thread with call SID if found
            if thread_context:
                thread_manager.update_thread_status(
                    thread_context.thread_id,
                    ThreadStatus.IN_CONVERSATION,
                    call_sid=call_sid,
                )

        # Use thread-specific agent or fallback to default
        if thread_context and thread_context.agent_instance:
            current_agent = thread_context.agent_instance
            current_voice_service = thread_context.voice_service
            print(f"🎯 Using thread-specific agent for {thread_context.customer_name}")
        else:
            current_agent = agent
            current_voice_service = voice_service
            print("⚠️ Using default agent (thread not found)")

        # Generate dynamic welcome message using agent's first response
        welcome_text = current_agent.get_initial_greeting(to_number)

        # Log conversation if thread context exists
        if thread_context:
            thread_manager.add_conversation_log(
                thread_context.thread_id, welcome_text, is_agent=True
            )

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
        call_sid = request.form.get("CallSid")
        speech_result = request.form.get("SpeechResult", "")

        print(f"🎤 User response ({to_number}): '{speech_result}'")

        # Find thread context for this call
        thread_context = None

        if call_sid:
            thread_context = thread_manager.get_thread_by_call_sid(call_sid)

        if not thread_context and to_number:
            thread_context = thread_manager.get_thread_by_phone(to_number)

        # Use thread-specific agent or fallback to default
        if thread_context and thread_context.agent_instance:
            current_agent = thread_context.agent_instance
            current_voice_service = thread_context.voice_service

            # Log user input
            thread_manager.add_conversation_log(
                thread_context.thread_id, speech_result, is_agent=False
            )
        else:
            current_agent = agent
            current_voice_service = voice_service
            print("⚠️ Using default agent (thread not found)")

        agent_response_text = current_agent.process_conversation(
            speech_result, to_number
        )

        # Log agent response if thread context exists
        if thread_context:
            thread_manager.add_conversation_log(
                thread_context.thread_id, agent_response_text, is_agent=True
            )

        # Check if conversation should end
        is_final = (
            "sms" in agent_response_text.lower()
            or "sending" in agent_response_text.lower()
            or "goodbye" in agent_response_text.lower()
        )

        if is_final:
            # Update thread status to completed if thread exists
            if thread_context:
                thread_manager.update_thread_status(
                    thread_context.thread_id, ThreadStatus.COMPLETED
                )

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

            # Check if this is a backend payload or legacy format
            if "agent" in data and "business" in data:
                # This is a backend payload - process through thread manager
                return handle_backend_payload(data)
            else:
                # This is legacy format - handle directly
                return handle_legacy_call(data)

        except Exception as e:
            print(f"❌ Error in start_call_endpoint: {str(e)}")
            return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

    def handle_backend_payload(payload):
        """Handle backend abandoned cart payload"""
        try:
            print("📦 Processing backend payload through ThreadManager")

            # Process payload through thread manager
            result = thread_manager.process_payload(payload)

            if result["success"]:
                return jsonify(
                    {
                        "success": True,
                        "thread_id": result["thread_id"],
                        "message": result["message"],
                        "customer_phone": result["customer_phone"],
                        "customer_name": result["customer_name"],
                        "system": "thread-based",
                    }
                )
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": result["error"],
                            "system": "thread-based",
                        }
                    ),
                    400,
                )

        except Exception as e:
            print(f"❌ Error processing backend payload: {str(e)}")
            return (
                jsonify({"error": f"Backend payload processing failed: {str(e)}"}),
                500,
            )

    def handle_legacy_call(data):
        """Handle legacy call format for backward compatibility"""
        try:
            # Validate required fields
            required_fields = ["phone_number", "business_info"]
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"{field} is required"}), 400

            # Convert legacy format to payload format
            legacy_payload = {
                "phone_number": data["phone_number"],
                "customer_name": data.get("customer_name", "Customer"),
                "customer_type": data.get("customer_type", "regular"),
                "business": {
                    "name": data["business_info"]["company_name"],
                    "description": data["business_info"].get("description", ""),
                    "website": data["business_info"].get("website", ""),
                },
                "agent": {
                    "name": data.get("agent_name", "AI Assistant"),
                    "tts_provider": data.get("tts_provider", "elevenlabs"),
                    "language": data.get("language", "en-US"),
                    "voice_settings": data.get("voice_settings", {}),
                },
            }

            print(f"🔄 Converting legacy call to thread-based system")
            print(f"📱 Phone: {legacy_payload['phone_number']}")
            print(f"🏢 Business: {legacy_payload['business']['name']}")

            # Process through thread manager
            result = thread_manager.process_payload(legacy_payload)

            if result["success"]:
                return jsonify(
                    {
                        "success": True,
                        "thread_id": result["thread_id"],
                        "call_sid": None,  # Will be set when call starts
                        "message": "AI agent call started successfully (thread-based)",
                        "config": {
                            "phone_number": result["customer_phone"],
                            "business": legacy_payload["business"]["name"],
                            "agent_name": legacy_payload["agent"]["name"],
                            "tts_provider": legacy_payload["agent"]["tts_provider"],
                        },
                        "system": "thread-based",
                    }
                )
            else:
                return jsonify({"error": result["error"]}), 500

        except Exception as e:
            print(f"❌ Error in legacy call handling: {str(e)}")
            return jsonify({"error": f"Failed to start call: {str(e)}"}), 500

    @app.route("/make-call", methods=["POST"])
    def make_call_endpoint():
        """Legacy API endpoint for simple outbound calls"""
        data = request.get_json()
        phone_number = data.get("phone_number")
        if not phone_number:
            return {"error": "phone_number is required"}, 400
        result = agent.make_outbound_call(phone_number)
        return result

    # Thread management endpoints
    @app.route("/threads", methods=["GET"])
    def get_all_threads():
        """Get status of all active threads"""
        try:
            return jsonify(thread_manager.get_all_threads_status())
        except Exception as e:
            return jsonify({"error": f"Failed to get threads: {str(e)}"}), 500

    @app.route("/threads/<thread_id>", methods=["GET"])
    def get_thread_status(thread_id):
        """Get status of specific thread"""
        status = thread_manager.get_thread_status(thread_id)
        if status:
            return jsonify(status)
        else:
            return jsonify({"error": "Thread not found"}), 404

    @app.route("/threads/<thread_id>/cancel", methods=["POST"])
    def cancel_thread(thread_id):
        """Cancel a specific thread"""
        success = thread_manager.cancel_thread(thread_id)
        if success:
            return jsonify(
                {"success": True, "message": f"Thread {thread_id} cancelled"}
            )
        else:
            return jsonify({"error": "Thread not found or cannot be cancelled"}), 404

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint"""
        thread_stats = thread_manager.get_all_threads_status()
        return jsonify(
            {
                "status": "healthy",
                "tts_provider": type(voice_service.tts_provider).__name__,
                "thread_system": "active",
                "active_threads": thread_stats["total_threads"],
                "thread_status_summary": thread_stats["status_summary"],
            }
        )

    return app
