"""
Thread Manager for Voice Agent System
Manages concurrent voice agent threads for multiple customers
"""

import threading
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import time

from agents.ecommerce.abandoned_cart_agent.agent import AbandonedCartAgent
from services.voice_service import VoiceService
from config.voice_config import VoiceConfig
from core.payload_processor import PayloadProcessor, ProcessedPayload


class ThreadStatus(Enum):
    """Thread status enumeration"""

    PENDING = "pending"
    ACTIVE = "active"
    CALLING = "calling"
    IN_CONVERSATION = "in_conversation"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ThreadContext:
    """Context information for each thread"""

    thread_id: str
    customer_phone: str
    customer_name: str
    customer_type: str
    agent_config: Dict[str, Any]
    business_info: Dict[str, Any]
    voice_service: VoiceService
    agent_instance: Optional[AbandonedCartAgent] = None
    status: ThreadStatus = ThreadStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    call_sid: Optional[str] = None
    error_message: Optional[str] = None
    conversation_log: list = field(default_factory=list)
    thread_object: Optional[threading.Thread] = None


class ThreadManager:
    """
    Manages concurrent voice agent threads
    Each thread handles one customer interaction
    """

    def __init__(self):
        self.active_threads: Dict[str, ThreadContext] = {}
        self.thread_lock = threading.Lock()
        self.max_concurrent_threads = 10  # Configurable limit
        self.payload_processor = PayloadProcessor()

        print("🧵 ThreadManager initialized")
        print(f"📊 Max concurrent threads: {self.max_concurrent_threads}")

    def process_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming payload and start a new thread
        Updated to handle the new backend payload structure

        Args:
            payload: Complete abandoned cart payload from backend

        Returns:
            Dict containing thread information
        """
        try:
            print(f"📦 Processing new payload...")

            # Extract and validate customer data
            customer_data = payload.get("customer", {})
            if not customer_data:
                return {
                    "success": False,
                    "error": "Missing customer data in payload",
                    "thread_id": None,
                }

            customer_phone = customer_data.get("phone", "").strip()
            if not customer_phone:
                return {
                    "success": False,
                    "error": "Customer phone number is required",
                    "thread_id": None,
                }

            customer_name = (
                customer_data.get("name")
                or f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
            )
            if not customer_name:
                customer_name = "Valued Customer"

            # Validate business data
            business_data = payload.get("business", {})
            if not business_data.get("name"):
                return {
                    "success": False,
                    "error": "Business name is required in payload",
                    "thread_id": None,
                }

            # Validate agent data
            agent_data = payload.get("agent", {})
            if not agent_data:
                return {
                    "success": False,
                    "error": "Agent configuration is required in payload",
                    "thread_id": None,
                }

            # Validate cart data
            cart_data = payload.get("abandoned_cart", {})
            if not cart_data or not cart_data.get("products"):
                return {
                    "success": False,
                    "error": "Abandoned cart data with products is required",
                    "thread_id": None,
                }

            print(f"✅ Payload validation successful")
            print(f"👤 Customer: {customer_name} ({customer_phone})")
            print(f"🏢 Business: {business_data.get('name')}")
            print(
                f"🛒 Cart Value: {cart_data.get('currency', 'USD')} {cart_data.get('total_value', 0)}"
            )

            # Check concurrent thread limit
            if len(self.active_threads) >= self.max_concurrent_threads:
                return {
                    "success": False,
                    "error": f"Maximum concurrent threads ({self.max_concurrent_threads}) reached",
                    "thread_id": None,
                }

            # Generate unique thread ID
            thread_id = f"thread_{uuid.uuid4().hex[:8]}"

            # Create voice service configuration
            voice_service = self._create_voice_service_from_payload(payload)

            # Create agent configuration for voice agent
            agent_config = self._create_agent_config_from_payload(payload)

            # Create thread context
            thread_context = ThreadContext(
                thread_id=thread_id,
                customer_phone=customer_phone,
                customer_name=customer_name,
                customer_type=customer_data.get("customer_type", "returning"),
                agent_config=agent_config,
                business_info={
                    "name": business_data.get("name"),
                    "description": business_data.get("description", ""),
                    "website": business_data.get("website", ""),
                    "phone": business_data.get("phone", ""),
                    "timezone": business_data.get("timezone", "UTC"),
                },
                voice_service=voice_service,
            )

            # Store thread context
            with self.thread_lock:
                self.active_threads[thread_id] = thread_context

            print(
                f"🆕 Created thread {thread_id} for {customer_name} ({customer_phone})"
            )

            # Start the thread
            success = self._start_voice_agent_thread(thread_id, payload)

            if success:
                return {
                    "success": True,
                    "thread_id": thread_id,
                    "customer_phone": customer_phone,
                    "customer_name": customer_name,
                    "message": f"Voice agent thread started for {customer_name}",
                }
            else:
                # Clean up failed thread
                with self.thread_lock:
                    if thread_id in self.active_threads:
                        del self.active_threads[thread_id]

                return {
                    "success": False,
                    "error": "Failed to start voice agent thread",
                    "thread_id": thread_id,
                }

        except Exception as e:
            print(f"❌ Error processing payload: {str(e)}")
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "error": f"Payload processing failed: {str(e)}",
                "thread_id": None,
            }

    def _create_voice_service_from_payload(
        self, payload: Dict[str, Any]
    ) -> VoiceService:
        """Create voice service based on payload configuration"""
        try:
            voice_config = payload.get("voice_config", {})
            agent_data = payload.get("agent", {})

            tts_provider = (
                voice_config.get("provider")
                or agent_data.get("tts_provider", "elevenlabs")
            ).lower()

            # Extract voice_id from payload
            voice_id = (
                voice_config.get("voice_id_external")
                or voice_config.get("voice_id")
                or agent_data.get("selected_voice_id")
                or agent_data.get("voice_id")
            )

            print(f"🎤 Extracted voice_id from payload: {voice_id}")

            # Create appropriate voice service
            if tts_provider == "elevenlabs":
                import os

                if os.getenv("ELEVENLABS_API_KEY"):
                    return VoiceConfig.create_elevenlabs_config(voice_id=voice_id)
                else:
                    print("⚠️ ElevenLabs API key not found, falling back to Twilio")
                    return VoiceConfig.create_twilio_config()
            else:
                return VoiceConfig.create_twilio_config()

        except Exception as e:
            print(f"⚠️ Error creating voice service: {str(e)}, using default Twilio")
            return VoiceConfig.create_twilio_config()

    def _create_voice_service_from_processed(
        self, processed_payload: ProcessedPayload
    ) -> VoiceService:
        """Create voice service based on processed payload configuration (legacy support)"""
        try:
            tts_provider = processed_payload.agent.tts_provider.lower()
            voice_id = processed_payload.agent.voice_id

            print(f"🎤 Extracted voice_id from processed payload: {voice_id}")

            # Create appropriate voice service
            if tts_provider == "elevenlabs":
                import os

                if os.getenv("ELEVENLABS_API_KEY"):
                    return VoiceConfig.create_elevenlabs_config(voice_id=voice_id)
                else:
                    print("⚠️ ElevenLabs API key not found, falling back to Twilio")
                    return VoiceConfig.create_twilio_config()
            else:
                return VoiceConfig.create_twilio_config()

        except Exception as e:
            print(f"⚠️ Error creating voice service: {str(e)}, using default Twilio")
            return VoiceConfig.create_twilio_config()

    def _create_voice_service(self, payload: Dict[str, Any]) -> VoiceService:
        """Create voice service based on payload configuration (legacy)"""
        try:
            # Get TTS provider and voice_id from payload
            agent_config = payload.get("agent", {})
            tts_provider = agent_config.get("tts_provider", "elevenlabs")
            voice_id = agent_config.get("selected_voice_id") or agent_config.get(
                "voice_id"
            )

            print(f"🎤 Extracted voice_id from legacy payload: {voice_id}")

            # Create appropriate voice service
            if tts_provider.lower() == "elevenlabs":
                import os

                if os.getenv("ELEVENLABS_API_KEY"):
                    return VoiceConfig.create_elevenlabs_config(voice_id=voice_id)
                else:
                    print("⚠️ ElevenLabs API key not found, falling back to Twilio")
                    return VoiceConfig.create_twilio_config()
            else:
                return VoiceConfig.create_twilio_config()

        except Exception as e:
            print(f"⚠️ Error creating voice service: {str(e)}, using default Twilio")
            return VoiceConfig.create_twilio_config()

    def _create_agent_config_from_payload(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create agent configuration from payload"""
        try:
            agent_data = payload.get("agent", {})
            business_data = payload.get("business", {})
            customer_data = payload.get("customer", {})
            cart_data = payload.get("abandoned_cart", {})
            voice_config = payload.get("voice_config", {})

            # Create comprehensive agent config
            agent_config = {
                # Basic agent info
                "agent_id": agent_data.get("id"),
                "agent_name": agent_data.get("name", "AI Assistant"),
                "agent_type": agent_data.get("type", "abandoned_cart_recovery"),
                # Voice configuration
                "tts_provider": agent_data.get("tts_provider", "elevenlabs"),
                "voice_id": (
                    voice_config.get("voice_id_external")
                    or voice_config.get("voice_id")
                    or agent_data.get("selected_voice_id")
                    or agent_data.get("voice_id")
                ),
                "language": voice_config.get("language", "en-US"),
                # Business context
                "business_name": business_data.get("name"),
                "business_website": business_data.get("website"),
                "business_phone": business_data.get("phone"),
                # Customer context
                "customer_name": customer_data.get("name")
                or f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
                "customer_phone": customer_data.get("phone"),
                "customer_email": customer_data.get("email"),
                "customer_type": customer_data.get("customer_type", "returning"),
                # Cart context
                "cart_id": cart_data.get("id"),
                "cart_total": cart_data.get("total_value", 0),
                "cart_currency": cart_data.get("currency", "USD"),
                "cart_url": cart_data.get("cart_url"),
                "cart_products": cart_data.get("products", []),
                "abandoned_at": cart_data.get("abandoned_at"),
                "recovery_attempts": cart_data.get("recovery_attempts", 0),
                # Conversation settings
                "personality": agent_data.get("personality", "friendly and helpful"),
                "conversation_style": agent_data.get(
                    "conversation_style", "professional yet casual"
                ),
                "max_conversation_length": 300,  # seconds
                # System settings
                "timezone": business_data.get("timezone", "UTC"),
                "template_slug": agent_data.get(
                    "template_slug", "ecommerce-abandoned-cart"
                ),
            }

            return agent_config

        except Exception as e:
            print(f"⚠️ Error creating agent config: {str(e)}")
            # Return minimal config
            return {
                "agent_name": "AI Assistant",
                "tts_provider": "elevenlabs",
                "customer_name": "Valued Customer",
                "business_name": "Our Store",
            }

    def _start_voice_agent_thread(
        self, thread_id: str, payload: Dict[str, Any]
    ) -> bool:
        """Start a new voice agent thread with updated payload structure"""
        try:
            thread_context = self.active_threads.get(thread_id)
            if not thread_context:
                return False

            # Use the agent config from thread context
            agent_config = thread_context.agent_config

            print(
                f"📝 Starting voice agent thread {thread_id} with config: {agent_config}"
            )

            # Create agent instance
            agent = AbandonedCartAgent(thread_context.voice_service, agent_config)
            thread_context.agent_instance = agent

            # Create and start thread - optimized for faster response
            def voice_agent_worker():
                try:
                    print(f"🎯 Starting voice agent for thread {thread_id}")

                    # Update thread status immediately
                    thread_context.status = ThreadStatus.ACTIVE
                    thread_context.started_at = datetime.now()

                    # Make the call asynchronously - don't block the response
                    try:
                        result = agent.make_outbound_call(
                            to_number=thread_context.customer_phone,
                            customer_name=thread_context.customer_name,
                        )

                        if result["success"]:
                            thread_context.call_sid = result["call_sid"]
                            thread_context.status = ThreadStatus.CALLING

                            print(
                                f"✅ Call started successfully for thread {thread_id}, Call SID: {result['call_sid']}"
                            )

                        else:
                            thread_context.status = ThreadStatus.FAILED
                            thread_context.error_message = result.get(
                                "error", "Call failed"
                            )
                            print(
                                f"❌ Call failed for thread {thread_id}: {thread_context.error_message}"
                            )

                    except Exception as call_error:
                        thread_context.status = ThreadStatus.FAILED
                        thread_context.error_message = (
                            f"Call initiation failed: {str(call_error)}"
                        )
                        print(
                            f"❌ Call initiation error for thread {thread_id}: {str(call_error)}"
                        )

                except Exception as e:
                    thread_context.status = ThreadStatus.FAILED
                    thread_context.error_message = str(e)
                    print(f"❌ Thread {thread_id} failed: {str(e)}")

                finally:
                    # Mark completion time
                    thread_context.completed_at = datetime.now()

                    # Clean up after some time (optional)
                    threading.Timer(
                        300.0, self._cleanup_thread, [thread_id]
                    ).start()  # 5 minutes

            # Start the thread immediately and return quickly
            worker_thread = threading.Thread(target=voice_agent_worker, daemon=True)
            thread_context.thread_object = worker_thread

            # Pre-set status to active before starting
            thread_context.status = ThreadStatus.ACTIVE
            thread_context.started_at = datetime.now()

            worker_thread.start()

            # Return immediately without waiting for call completion
            return True

        except Exception as e:
            print(f"❌ Error starting thread {thread_id}: {str(e)}")
            return False

    def get_thread_status(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific thread"""
        with self.thread_lock:
            thread_context = self.active_threads.get(thread_id)
            if not thread_context:
                return None

            return {
                "thread_id": thread_id,
                "customer_phone": thread_context.customer_phone,
                "customer_name": thread_context.customer_name,
                "status": thread_context.status.value,
                "created_at": thread_context.created_at.isoformat(),
                "started_at": (
                    thread_context.started_at.isoformat()
                    if thread_context.started_at
                    else None
                ),
                "completed_at": (
                    thread_context.completed_at.isoformat()
                    if thread_context.completed_at
                    else None
                ),
                "call_sid": thread_context.call_sid,
                "error_message": thread_context.error_message,
                "conversation_length": len(thread_context.conversation_log),
            }

    def get_all_threads_status(self) -> Dict[str, Any]:
        """Get status of all threads - optimized for speed"""
        try:
            with self.thread_lock:
                # Quick summary without detailed thread info for speed
                total_threads = len(self.active_threads)
                status_summary = self._get_status_summary()

                # Only get detailed info if there are few threads
                if total_threads <= 5:
                    threads = [
                        self.get_thread_status(tid)
                        for tid in self.active_threads.keys()
                    ]
                else:
                    # For many threads, just return basic info
                    threads = [
                        {
                            "thread_id": tid,
                            "customer_name": ctx.customer_name,
                            "status": ctx.status.value,
                            "customer_phone": ctx.customer_phone,
                        }
                        for tid, ctx in list(self.active_threads.items())[
                            :10
                        ]  # Limit to 10
                    ]

                return {
                    "total_threads": total_threads,
                    "threads": threads,
                    "status_summary": status_summary,
                }
        except Exception as e:
            print(f"❌ Error getting threads status: {str(e)}")
            return {
                "total_threads": 0,
                "threads": [],
                "status_summary": {},
                "error": str(e),
            }

    def _get_status_summary(self) -> Dict[str, int]:
        """Get summary of thread statuses"""
        summary = {}
        for thread_context in self.active_threads.values():
            status = thread_context.status.value
            summary[status] = summary.get(status, 0) + 1
        return summary

    def get_thread_by_call_sid(self, call_sid: str) -> Optional[ThreadContext]:
        """Find thread by Twilio Call SID"""
        with self.thread_lock:
            for thread_context in self.active_threads.values():
                if thread_context.call_sid == call_sid:
                    return thread_context
        return None

    def get_thread_by_phone(self, phone_number: str) -> Optional[ThreadContext]:
        """Find active thread by phone number"""
        with self.thread_lock:
            for thread_context in self.active_threads.values():
                if (
                    thread_context.customer_phone == phone_number
                    and thread_context.status
                    in [
                        ThreadStatus.ACTIVE,
                        ThreadStatus.CALLING,
                        ThreadStatus.IN_CONVERSATION,
                    ]
                ):
                    return thread_context
        return None

    def update_thread_status(self, thread_id: str, status: ThreadStatus, **kwargs):
        """Update thread status and additional information"""
        with self.thread_lock:
            thread_context = self.active_threads.get(thread_id)
            if thread_context:
                thread_context.status = status

                # Update additional fields
                for key, value in kwargs.items():
                    if hasattr(thread_context, key):
                        setattr(thread_context, key, value)

                print(f"📊 Thread {thread_id} status updated to {status.value}")

    def add_conversation_log(
        self, thread_id: str, message: str, is_agent: bool = False
    ):
        """Add message to thread conversation log"""
        with self.thread_lock:
            thread_context = self.active_threads.get(thread_id)
            if thread_context:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "message": message,
                    "is_agent": is_agent,
                }
                thread_context.conversation_log.append(log_entry)

    def _cleanup_thread(self, thread_id: str):
        """Clean up completed thread after timeout"""
        with self.thread_lock:
            thread_context = self.active_threads.get(thread_id)
            if thread_context and thread_context.status in [
                ThreadStatus.COMPLETED,
                ThreadStatus.FAILED,
                ThreadStatus.CANCELLED,
            ]:
                print(f"🧹 Cleaning up thread {thread_id}")
                del self.active_threads[thread_id]

    def cancel_thread(self, thread_id: str) -> bool:
        """Cancel a specific thread"""
        with self.thread_lock:
            thread_context = self.active_threads.get(thread_id)
            if thread_context:
                thread_context.status = ThreadStatus.CANCELLED
                thread_context.completed_at = datetime.now()
                print(f"🚫 Thread {thread_id} cancelled")
                return True
        return False

    def shutdown(self):
        """Shutdown thread manager and clean up all threads"""
        print("🔄 Shutting down ThreadManager...")

        with self.thread_lock:
            for thread_id, thread_context in self.active_threads.items():
                if thread_context.status in [
                    ThreadStatus.ACTIVE,
                    ThreadStatus.CALLING,
                    ThreadStatus.IN_CONVERSATION,
                ]:
                    thread_context.status = ThreadStatus.CANCELLED
                    print(f"🚫 Cancelled thread {thread_id}")

            self.active_threads.clear()

        print("✅ ThreadManager shutdown complete")


# Global thread manager instance
_thread_manager: Optional[ThreadManager] = None


def get_thread_manager() -> ThreadManager:
    """Get or create global thread manager instance"""
    global _thread_manager
    if _thread_manager is None:
        _thread_manager = ThreadManager()
    return _thread_manager
