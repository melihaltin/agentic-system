"""
Flask webhook server for Twilio voice integration
Thread-based system supporting concurrent customer interactions
"""

import os
from typing import Dict, Any
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

    def detect_payload_type(payload: Dict[str, Any]) -> str:
        """Detect the type of incoming payload"""
        if not payload:
            return "empty"

        # Backend abandoned cart payload format (most specific)
        # Check for the exact structure: agent + company + platforms + voice_config + metadata
        if all(key in payload for key in ["agent", "company", "platforms"]) and any(
            key in payload for key in ["voice_config", "metadata", "summary"]
        ):
            return "backend_abandoned_cart"

        # Simpler backend format (agent + company)
        if "agent" in payload and "company" in payload:
            return "backend_abandoned_cart"

        # Legacy API format
        if "phone_number" in payload and "business_info" in payload:
            return "legacy_api"

        # Direct abandoned cart format
        if "abandoned_carts" in payload:
            return "abandoned_cart_direct"

        # Generic format with customer info
        if "customer" in payload or "agent" in payload:
            return "generic"

        return "unknown"

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
            print("🚀 /start-call request received")
            data = request.get_json()
            print(
                f"📨 Payload received with keys: {list(data.keys()) if data else 'None'}"
            )

            if not data:
                return jsonify({"error": "No payload received"}), 400

            # Validate required fields
            required_fields = ["agent", "company", "platforms"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return (
                    jsonify(
                        {
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        }
                    ),
                    400,
                )

            # Check if there are any abandoned carts
            platforms = data.get("platforms", {})
            has_carts = any(
                platform_data.get("abandoned_carts")
                for platform_data in platforms.values()
            )

            if not has_carts:
                return jsonify({"error": "No abandoned carts found in payload"}), 400

            print(f"data: {data}")
            return handle_backend_payload(data)

        except Exception as e:
            print(f"❌ Error in start_call_endpoint: {str(e)}")
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

    def handle_backend_payload(payload):
        """Handle backend abandoned cart payload"""
        try:
            print("📦 Processing backend payload through ThreadManager")

            # Log key payload information for debugging
            agent_info = payload.get("agent", {})
            company_info = payload.get("company", {})
            voice_config = payload.get("voice_config", {})
            platforms = payload.get("platforms", {})

            print(
                f"🤖 Agent: {agent_info.get('name', 'Unknown')} (ID: {agent_info.get('id', 'N/A')})"
            )
            print(
                f"🏢 Company: {company_info.get('name', 'Unknown')} (ID: {company_info.get('id', 'N/A')})"
            )
            print(
                f"🎤 Voice: {voice_config.get('name', 'Default')} ({voice_config.get('provider', 'Unknown')})"
            )
            print(f"🛒 Platforms: {list(platforms.keys()) if platforms else 'None'}")

            # Extract abandoned cart information for logging
            total_carts = 0
            total_value = 0.0
            customer_names = []
            processed_customers = []

            for platform_name, platform_data in platforms.items():
                if "abandoned_carts" in platform_data:
                    carts = platform_data["abandoned_carts"]
                    total_carts += len(carts)

                    for cart in carts:
                        total_value += cart.get("total_value", 0)
                        customer = cart.get("customer", {})
                        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                        if customer_name:
                            customer_names.append(customer_name)

                        # Prepare customer data for processing
                        processed_customers.append(
                            {
                                "customer": customer,
                                "cart": cart,
                                "platform": platform_name,
                            }
                        )

            print(f"📊 Found {total_carts} abandoned cart(s) worth ${total_value:.2f}")
            if customer_names:
                print(
                    f"👥 Customers: {', '.join(customer_names[:3])}{'...' if len(customer_names) > 3 else ''}"
                )

            # Process each customer separately (since ThreadManager handles one customer at a time)
            results = []

            for customer_data in processed_customers:
                # Transform the payload structure to match what ThreadManager expects
                transformed_payload = transform_payload_structure(
                    payload, customer_data
                )

                # Process payload through thread manager
                result = thread_manager.process_payload(transformed_payload)

                if result["success"]:
                    print(f"✅ Thread created successfully: {result['thread_id']}")
                    results.append(
                        {
                            "success": True,
                            "thread_id": result["thread_id"],
                            "message": result["message"],
                            "customer_phone": result["customer_phone"],
                            "customer_name": result["customer_name"],
                            "warnings": result.get("warnings"),
                        }
                    )
                else:
                    print(f"❌ Thread creation failed: {result['error']}")
                    results.append(
                        {
                            "success": False,
                            "error": result["error"],
                            "customer_phone": customer_data["customer"].get(
                                "phone", "Unknown"
                            ),
                            "customer_name": f"{customer_data['customer'].get('first_name', '')} {customer_data['customer'].get('last_name', '')}".strip(),
                        }
                    )

            # Return consolidated results
            successful_threads = [r for r in results if r["success"]]
            failed_threads = [r for r in results if not r["success"]]

            return jsonify(
                {
                    "success": len(successful_threads) > 0,
                    "total_customers": len(processed_customers),
                    "successful_threads": len(successful_threads),
                    "failed_threads": len(failed_threads),
                    "threads": successful_threads,
                    "failures": failed_threads if failed_threads else None,
                    "system": "thread-based",
                    "payload_info": {
                        "agent_name": agent_info.get("name"),
                        "company_name": company_info.get("name"),
                        "tts_provider": agent_info.get("tts_provider"),
                        "voice_provider": voice_config.get("provider"),
                        "abandoned_carts_count": total_carts,
                        "total_cart_value": total_value,
                    },
                }
            )

        except Exception as e:
            print(f"❌ Error processing backend payload: {str(e)}")
            import traceback

            traceback.print_exc()
            return (
                jsonify({"error": f"Backend payload processing failed: {str(e)}"}),
                500,
            )

    def transform_payload_structure(original_payload, customer_data):
        """
        Transform the backend payload structure to match what PayloadProcessor expects
        """
        customer = customer_data["customer"]
        cart = customer_data["cart"]
        platform = customer_data["platform"]

        agent_info = original_payload.get("agent", {})
        company_info = original_payload.get("company", {})
        voice_config = original_payload.get("voice_config", {})

        # Transform to expected structure
        transformed = {
            # Customer information
            "customer": {
                "id": customer.get("id"),
                "email": customer.get("email"),
                "first_name": customer.get("first_name", ""),
                "last_name": customer.get("last_name", ""),
                "phone": customer.get("phone", ""),
                "name": f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                "customer_type": "returning" if customer.get("created_at") else "new",
                "created_at": customer.get("created_at"),
            },
            # Business information
            "business": {
                "name": company_info.get("name", ""),
                "description": f"{company_info.get('business_category', 'E-commerce')} business",
                "website": company_info.get("website", ""),
                "phone": company_info.get("phone_number", ""),
                "timezone": company_info.get("timezone", "America/Denver"),
            },
            # Agent configuration
            "agent": {
                "id": agent_info.get("id"),
                "name": agent_info.get("name", "AI Assistant"),
                "type": agent_info.get("type", "abandoned_cart_recovery"),
                "template_slug": agent_info.get(
                    "template_slug", "ecommerce-abandoned-cart"
                ),
                "tts_provider": agent_info.get("tts_provider", "elevenlabs"),
                "voice_id": voice_config.get("voice_id_external")
                or agent_info.get("selected_voice_id"),
                "language": voice_config.get("language", "en-US"),
                "personality": "friendly and helpful",
                "conversation_style": "professional yet casual",
            },
            # Cart and product information
            "abandoned_cart": {
                "id": cart.get("id"),
                "total_value": cart.get("total_value", 0),
                "currency": cart.get("currency", "USD"),
                "abandoned_at": cart.get("abandoned_at"),
                "recovery_attempts": cart.get("recovery_attempts", 0),
                "cart_url": cart.get("cart_url", ""),
                "platform": platform,
                "status": cart.get("status", "abandoned"),
                "products": cart.get("products", []),
            },
            # Voice configuration
            "voice_config": {
                "provider": voice_config.get("provider", "elevenlabs"),
                "voice_id": voice_config.get("voice_id_external")
                or agent_info.get("selected_voice_id"),
                "language": voice_config.get("language", "en-US"),
                "name": voice_config.get("name", "AI Assistant"),
            },
            # Platform information
            "platform_data": {
                platform: original_payload.get("platforms", {}).get(platform, {})
            },
            # Metadata
            "metadata": {
                "generated_at": original_payload.get("metadata", {}).get(
                    "generated_at"
                ),
                "payload_version": original_payload.get("metadata", {}).get(
                    "payload_version", "1.0"
                ),
                "service": original_payload.get("metadata", {}).get(
                    "service", "abandoned_cart_recovery"
                ),
                "mock_data": original_payload.get("platforms", {})
                .get(platform, {})
                .get("mock_data", False),
            },
        }

        return transformed

    @app.route("/make-call", methods=["POST"])
    def make_call_endpoint():
        """Legacy API endpoint for simple outbound calls"""
        data = request.get_json()
        print(f"📞 Legacy make-call request: {data}")
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
