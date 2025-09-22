"""
Twilio Outbound Voice Agent - Fixed
"""

import os
import json
from typing import Dict, Any
from datetime import datetime

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Twilio imports - Fixed import
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

from services.voice_service import VoiceService
from services.tts.elevenlabs import ElevenLabsTTS


class AbandonedCartAgent:
    """Twilio outbound voice agent with LangGraph integration"""

    def __init__(self, voice_service: VoiceService, call_config: Dict[str, Any] = None):
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        self.voice_service = voice_service

        # Store call configuration for dynamic behavior
        self.call_config = call_config or {}

        # Configure LLM with tools
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.2,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

        # Create promo code tool with injected configuration
        self.promo_tool = self._create_promo_tool()
        self.llm_with_tools = self.llm.bind_tools([self.promo_tool])

        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.active_calls = {}

    def _create_promo_tool(self):
        """Create promo tool with injected call configuration"""
        from langchain_core.tools import tool

        # Get data from call config
        phone_number = self.call_config.get("phone_number", "")
        cart_id = self.call_config.get("cart_id", "")
        customer_type = self.call_config.get("customer_type", "regular")

        @tool
        def internal_generate_promo_code() -> Dict[str, Any]:
            """Generate a promo code for the customer and automatically send it via SMS.
            No parameters needed - all data comes from call configuration.

            Returns:
                Dict[str, Any]: Details of the generated promo code and SMS status.
            """
            import random
            import string
            from datetime import datetime

            print("🛠️ generate_promo_code tool called with injected config")

            # Use injected configuration data
            discount = (
                random.randint(15, 25)
                if customer_type == "VIP"
                else random.randint(10, 20)
            )
            prefix = "VIP" if customer_type == "VIP" else "SAVE"

            suffix = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
            promo_code = f"{prefix}{suffix}"

            promo_data = {
                "promo_code": promo_code,
                "discount_percent": discount,
                "cart_id": cart_id or "N/A",
                "customer_type": customer_type,
                "valid_until": "2025-12-31",
                "generated_at": datetime.now().isoformat(),
            }

            # Send SMS using injected phone number
            if phone_number:
                sms_sent = self._send_promo_sms(phone_number, promo_data)
                promo_data["sms_sent"] = sms_sent
                print(
                    f"✅ Promo code generated and SMS sent: {promo_code} (%{discount} discount)"
                )
            else:
                promo_data["sms_sent"] = False
                print(f"⚠️ Promo code generated but missing phone number: {promo_code}")

            return promo_data

        return internal_generate_promo_code

    def _send_promo_sms(self, phone_number: str, promo_data: Dict[str, Any]) -> bool:
        """Send promo SMS"""
        try:
            message_body = f"""🎉 Your exclusive promo code is ready!
Code: {promo_data['promo_code']}
Discount: %{promo_data['discount_percent']}
Valid until: {promo_data['valid_until']}
Happy shopping! 🛍️"""

            message = self.twilio_client.messages.create(
                body=message_body, from_=self.twilio_phone, to=phone_number
            )
            print(f"📱 SMS sent: {phone_number} (SID: {message.sid})")
            return True
        except Exception as e:
            print(f"❌ SMS sending error: {str(e)}")
            return False

    def _create_dynamic_system_prompt(self) -> str:
        """Create dynamic system prompt based on call configuration."""
        if not self.call_config:
            return """
                You are a professional and friendly customer service representative. You understand all languages and will continue in whichever language the customer speaks. Your tasks:
                1. Politely greet the customer and offer a special promo code.
                2. If the customer is interested, respond positively (e.g., "Great!") and immediately call the `internal_generate_promo_code` tool.
                3. DO NOT ask for phone number or cart ID - you already have access to this information.
                4. After the tool runs, say "I am sending your promo code and details via SMS. Have a great day!" and end the conversation.
                Keep it simple and friendly!
            """

        # Extract configuration details
        business_info = self.call_config.get("business_info", {})
        customer_name = self.call_config.get("customer_name", "")
        agent_name = self.call_config.get("agent_name", "AI Assistant")
        customer_type = self.call_config.get("customer_type", "regular")

        # Extract cart data for personalized conversation
        cart_data = self.call_config.get("cart_data", [])
        platform_data = self.call_config.get("platform_data", {})

        company_name = business_info.get("company_name", "our company")
        company_description = business_info.get("description", "")
        company_website = business_info.get("website", "")

        # Build dynamic system prompt with cart details
        prompt_parts = [
            f"You are a professional and friendly AI customer service representative for {company_name}.",
            f"Your name is {agent_name}.",
        ]

        if company_description:
            prompt_parts.append(f"Company description: {company_description}")

        if company_website:
            prompt_parts.append(f"Company website: {company_website}")

        # Add customer-specific information
        prompt_parts.extend(
            [
                f"You are calling customer {customer_name if customer_name else 'the customer'}.",
                f"Customer type: {customer_type}",
            ]
        )

        # Add cart-specific details for personalized conversation
        if cart_data:
            total_cart_value = 0
            cart_items = []

            for cart in cart_data:
                cart_value = cart.get("total_value", 0)
                total_cart_value += cart_value

                items = cart.get("items", [])
                for item in items:
                    item_name = item.get("name") or item.get("title", "Unknown Product")
                    item_price = item.get("price", 0)
                    cart_items.append(f"{item_name} (${item_price})")

            if cart_items:
                prompt_parts.extend(
                    [
                        f"ABANDONED CART DETAILS:",
                        f"- Total cart value: ${total_cart_value:.2f}",
                        f"- Items in cart: {', '.join(cart_items[:3])}"
                        + ("..." if len(cart_items) > 3 else ""),
                    ]
                )

        # Add platform information
        if platform_data:
            platforms = list(platform_data.keys())
            if platforms:
                prompt_parts.append(f"Platform: {', '.join(platforms)}")

        prompt_parts.extend(
            [
                f"CONVERSATION GOAL: Help the customer complete their purchase by offering a personalized discount.",
                f"Customer type: {customer_type}",
                "You understand all languages and will continue in whichever language the customer speaks.",
                "Your conversation flow:",
                "1. Politely introduce yourself and the company, then offer a special promo code for their abandoned cart.",
                "2. If the customer is interested, respond positively and immediately call the `internal_generate_promo_code` tool.",
                "3. DO NOT ask for any personal information like phone number or cart ID - you already have access to all necessary information.",
                "4. After the tool runs, inform the customer that you're sending the promo code via SMS and end the conversation politely.",
                "Keep the conversation natural, friendly, and professional. Focus on the value of the offer, not on collecting information.",
            ]
        )

        return " ".join(prompt_parts)

    def _build_graph(self):
        """Build LangGraph workflow."""

        def agent_node(state: MessagesState):
            """Main node that talks to the customer and calls tools."""
            system_prompt = SystemMessage(content=self._create_dynamic_system_prompt())

            if len(state["messages"]) <= 1:
                messages = [system_prompt] + state["messages"]
            else:
                messages = state["messages"]

            # Handle initial call start
            last_message = state["messages"][-1]
            if (
                isinstance(last_message, HumanMessage)
                and last_message.content == "START_CALL"
            ):
                # Generate initial greeting
                business_name = (
                    self.call_config.get("business_info", {}).get(
                        "company_name", "our company"
                    )
                    if self.call_config
                    else "our company"
                )
                agent_name = (
                    self.call_config.get("agent_name", "AI Assistant")
                    if self.call_config
                    else "AI Assistant"
                )
                customer_name = self.call_config.get("customer_name", "")

                name_part = f", {customer_name}" if customer_name else ""
                greeting = f"Hello{name_part}! This is {agent_name} calling from {business_name}. I noticed you left some items in your cart, and I'd like to offer you an exclusive promotional code to complete your purchase. Would you be interested?"

                return {"messages": [AIMessage(content=greeting)]}

            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        tool_node = ToolNode([self.promo_tool])

        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)

        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {"tools": "tools", END: END},
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile(checkpointer=self.memory)

    def get_initial_greeting(self, phone_number: str) -> str:
        """Generate initial greeting message using AI agent."""
        if not self.call_config:
            return "Hello, I am calling to offer you a special promo code for your abandoned cart. Are you interested?"

        try:
            # Create thread for this specific call
            thread_id = f"call_{phone_number.strip().replace('+', '')}"
            config = {"configurable": {"thread_id": thread_id}}

            # Generate initial greeting using the agent
            response = self.graph.invoke(
                {"messages": [HumanMessage(content="START_CALL")]}, config=config
            )

            return response["messages"][-1].content

        except Exception as e:
            print(f"❌ Error generating greeting: {str(e)}")
            # Fallback to static message
            business_name = self.call_config.get("business_info", {}).get(
                "company_name", "our company"
            )
            agent_name = self.call_config.get("agent_name", "AI Assistant")
            customer_name = self.call_config.get("customer_name", "")
            name_part = f", {customer_name}" if customer_name else ""

            return f"Hello{name_part}, this is {agent_name} from {business_name}. I'm calling about your abandoned cart - I have a special promotional offer for you. Are you interested?"

    def make_outbound_call(
        self, to_number: str, customer_name: str = ""
    ) -> Dict[str, Any]:
        """Make an outbound call."""
        try:
            webhook_url = f"{os.getenv('WEBHOOK_BASE_URL')}/webhook/outbound/start"
            call = self.twilio_client.calls.create(
                to=to_number, from_=self.twilio_phone, url=webhook_url, method="POST"
            )
            self.active_calls[call.sid] = {
                "phone_number": to_number,
                "customer_name": customer_name,
                "status": "initiated",
                "started_at": datetime.now().isoformat(),
                "call_sid": call.sid,
            }
            print(f"✅ Outbound call started: {to_number} (SID: {call.sid})")
            return {"success": True, "call_sid": call.sid}
        except Exception as e:
            print(f"❌ Call error: {str(e)}")
            return {"success": False, "error": str(e)}

    def process_conversation(self, user_input: str, phone_number: str) -> str:
        """Process user input and get a response from the agent."""
        thread_id = f"call_{phone_number.strip().replace('+', '')}"
        config = {"configurable": {"thread_id": thread_id}}

        try:
            response = self.graph.invoke(
                {"messages": [HumanMessage(content=user_input)]}, config=config
            )

            last_message = response["messages"][-1]

            if last_message.tool_calls:
                tool_call = last_message.tool_calls[0]

                # Tool is called without any parameters since all config is injected
                tool_output = self.promo_tool.invoke({})

                final_response = self.graph.invoke(
                    {
                        "messages": [
                            ToolMessage(
                                content=json.dumps(tool_output),
                                tool_call_id=tool_call["id"],
                            )
                        ]
                    },
                    config=config,
                )

                return final_response["messages"][-1].content

            return last_message.content

        except Exception as e:
            print(f"❌ Conversation error: {str(e)}")
            return "Sorry, something went wrong. Let me send you that promo code anyway. Goodbye."

    def generate_voice_response(
        self, text: str, is_final: bool = False, gather_input: bool = True
    ) -> VoiceResponse:
        """Generate Twilio VoiceResponse with appropriate TTS"""
        response = VoiceResponse()

        # Check if using ElevenLabs or custom TTS
        if isinstance(self.voice_service.tts_provider, ElevenLabsTTS):
            try:
                # Generate audio URL with ElevenLabs
                audio_url = self.voice_service.text_to_speech(text)
                response.play(audio_url)
            except Exception as e:
                print(f"❌ ElevenLabs error, falling back to Twilio TTS: {e}")
                response.say(text, voice="Polly.Joanna", language="en-US")
        else:
            # Use Twilio's built-in TTS
            response.say(text, voice="Polly.Joanna", language="en-US")

        # Add gather for user input if not final
        if not is_final and gather_input:
            gather = Gather(
                input="speech dtmf",
                action="/webhook/outbound/process",
                method="POST",
                speechTimeout="auto",
                timeout=10,
            )
            response.append(gather)

            # Fallback if no input received
            response.say(
                "Thank you for your time. Have a great day!", voice="Polly.Joanna"
            )

        if is_final:
            response.hangup()

        return response
