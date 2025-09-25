"""
Twilio Outbound Voice Agent - Fixed
"""

import os
import json
from typing import Dict, Any, TypedDict
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
from langchain_core.tools import tool
from typing import List, Annotated
import operator
from langchain_core.messages import BaseMessage, SystemMessage


class AgentState(TypedDict):
    """
    Konuşma durumu için genişletilmiş yapı.

    Attributes:
        messages: Konuşmadaki mesajların listesi. `operator.add` ile her seferinde listeye ekleme yapılır.
        system_prompt: Bu konuşma için oluşturulan ve yeniden kullanılan sistem talimatı.
        should_end: Konuşmanın sonlanması gerekip gerekmediğini belirten flag.
    """

    messages: Annotated[List[BaseMessage], operator.add]
    system_prompt: str
    should_end: bool


class AbandonedCartAgent:

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
        self.end_conversation_tool = self._create_end_conversation_tool()
        self.llm_with_tools = self.llm.bind_tools(
            [self.promo_tool, self.end_conversation_tool]
        )

        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.active_calls = {}

    def _create_promo_tool(self):

        # Get data from call config - handle different field names
        phone_number = self.call_config.get("phone_number") or self.call_config.get(
            "customer_phone", ""
        )
        cart_id = self.call_config.get("cart_id", "")

        @tool
        def internal_generate_promo_code() -> str:
            """Generate a promo code for the customer and automatically send it via SMS.
            No parameters needed - all data comes from call configuration.

            Returns:
                str: Simple success message for the agent to interpret naturally.
            """
            import random
            import string
            from datetime import datetime

            print("🛠️ generate_promo_code tool called with injected config")

            # Use injected configuration data
            discount = random.randint(15, 25)
            prefix = "SAVE"

            suffix = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
            promo_code = f"{prefix}{suffix}"

            promo_data = {
                "promo_code": promo_code,
                "discount_percent": discount,
                "cart_id": cart_id or "N/A",
                "valid_until": "2025-12-31",
                "generated_at": datetime.now().isoformat(),
            }

            # Send SMS using injected phone number
            if phone_number:
                sms_sent = self._send_promo_sms(phone_number, promo_data)
                print(
                    f"✅ Promo code generated and SMS sent: {promo_code} (%{discount} discount)"
                )

                # Return simple, human-friendly message for the agent
                if sms_sent:
                    return f"Successfully created discount code {promo_code} with {discount}% discount and sent via SMS."
                else:
                    return f"Created discount code {promo_code} with {discount}% discount but SMS delivery failed."
            else:
                print(f"⚠️ Promo code generated but missing phone number: {promo_code}")
                return f"Created discount code {promo_code} with {discount}% discount but no phone number available for SMS."

        return internal_generate_promo_code

    def _create_end_conversation_tool(self):
        """Telefon görüşmesini sonlandırmak için AI'nın çağıracağı aracı oluşturur."""

        @tool
        def internal_end_conversation() -> str:
            """
            Call this tool to politely end the phone conversation. This should be used
            only when the user has clearly indicated the conversation is over,
            for example by saying 'goodbye', 'thank you, that's all', or 'I have no more questions'.
            """
            print("📞 End conversation tool called. Signaling to hang up.")
            return "Conversation has been marked to end."

        return internal_end_conversation

    def _send_promo_sms(self, phone_number: str, promo_data: Dict[str, Any]) -> bool:
        """Send promo SMS"""
        try:
            message_body = f"""🎉 Your exclusive promo code is ready!
Code: {promo_data['promo_code']}
Discount: %{promo_data['discount_percent']}
Valid until: {promo_data['valid_until']}
Happy shopping! 🛍️"""

            # message = self.twilio_client.messages.create(
            #     body=message_body, from_=self.twilio_phone, to=phone_number
            # )
            # print(f"📱 SMS sent: {phone_number} (SID: {message.sid})")
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
                4. IMPORTANT: After calling a tool, DO NOT read the technical output to the customer. Instead, interpret the results and respond naturally. For example:
                   - After promo tool: "Perfect! I've generated a special discount code for you and I'm sending it to your phone via SMS right now. You should receive it shortly."
                   - Keep responses conversational and human-friendly
                5. When ready to end, use natural language like "Have a great day!" and call the `internal_end_conversation` tool.
                Keep it simple, friendly, and never read technical data to customers!
            """

        print(f"📝 Building dynamic system prompt from call config {self.call_config}")
        # Extract configuration details - handle both nested and flat structures
        business_info = self.call_config.get("business_info", {})
        print(f"📝 Extracting business info: {business_info}")

        # Get customer name directly from config (flat structure)
        customer_name = self.call_config.get("customer_name", "")
        print(f"📝 Extracting customer name: {customer_name}")

        agent_name = self.call_config.get("agent_name", "AI Assistant")

        # Extract language configuration
        language = self.call_config.get("language", "English")
        print(f"📝 Extracting language: {language}")

        # Extract cart data for personalized conversation
        cart_data = self.call_config.get("cart_data", [])
        platform_data = self.call_config.get("platform_data", {})

        # Get company info - try nested structure first, then flat structure
        company_name = (
            business_info.get("company_name")
            or self.call_config.get("business_name")
            or "our company"
        )
        company_description = (
            business_info.get("description")
            or self.call_config.get("business_description")
            or ""
        )
        company_website = (
            business_info.get("website")
            or self.call_config.get("business_website")
            or ""
        )

        print(
            f"📝 Building system prompt for {company_name}, customer: {customer_name}"
            f", cart items: {len(cart_data)}, platform: {list(platform_data.keys()) if platform_data else 'N/A'}"
            f", language: {language}"
        )

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
            ]
        )

        # Add cart-specific details for personalized conversation
        # Handle both nested cart_data and flat cart structure
        cart_products = self.call_config.get("cart_products", [])
        cart_total = self.call_config.get("cart_total", 0)

        if cart_data:
            # Handle nested cart structure
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
        elif cart_products:
            # Handle flat cart structure from your config
            cart_items = []
            for product in cart_products:
                item_name = product.get("title") or product.get(
                    "name", "Unknown Product"
                )
                item_price = product.get("price", 0)
                cart_items.append(f"{item_name} (${item_price})")

            if cart_items:
                prompt_parts.extend(
                    [
                        f"ABANDONED CART DETAILS:",
                        f"- Total cart value: ${cart_total:.2f}",
                        f"- Items in cart: {', '.join(cart_items[:3])}"
                        + ("..." if len(cart_items) > 3 else ""),
                    ]
                )

        # Add platform information
        if platform_data:
            platforms = list(platform_data.keys())
            if platforms:
                prompt_parts.append(f"Platform: {', '.join(platforms)}")

        # Add language instructions
        prompt_parts.extend(
            [
                f"CONVERSATION GOAL: Help the customer complete their purchase by offering a personalized discount.",
                f"LANGUAGE INSTRUCTIONS:",
                f"- You MUST start the conversation in {language}.",
                f"- After starting in {language}, you should adapt to whatever language the customer responds in.",
                f"- If the customer switches to a different language, continue the conversation in their preferred language.",
                f"- You understand all languages and can communicate fluently in any language the customer chooses.",
            ]
        )

        prompt_parts.extend(
            [
                "Your conversation flow:",
                f"1. Politely introduce yourself and the company in {language}, then offer a special promo code for their abandoned cart.",
                "2. If the customer is interested, respond positively and immediately call the `internal_generate_promo_code` tool.",
                "3. DO NOT ask for any personal information like phone number or cart ID - you already have access to all necessary information.",
                "4. CRITICAL: After any tool runs, DO NOT read the technical output/JSON to the customer. Instead, interpret the results naturally:",
                "   - After promo tool success: 'Perfect! I've created a special discount code for you and I'm sending it to your phone via SMS right now. You should receive it within a few moments.'",
                "   - Keep all responses conversational and human-friendly, never technical",
                "5. Ask if there's anything else you can help them with after providing the promo code.",
                "6. IMPORTANT: When the customer indicates they want to end the conversation (saying goodbye, thank you, that's all, etc.), respond naturally (e.g., 'You're welcome! Have a wonderful day!') and then call the `internal_end_conversation` tool.",
                "Always speak naturally like a human customer service representative. Never read system data, JSON, or technical outputs to customers.",
            ]
        )

        prompt_string = " ".join(prompt_parts)

        print(f"📝 Final system prompt: {prompt_string}")

        return prompt_string

    def _build_graph(self):
        """
        LangGraph iş akışını düzeltilmiş conditional edge logic ile kurar.
        """

        def initialize_prompt_node(state: AgentState):
            """
            Grafiğin giriş noktası. Sistem talimatını yalnızca durum'da (state) mevcut değilse oluşturur.
            """
            # Sadece durum'da prompt yoksa (yani konuşmanın ilk adımıysa) oluştur.
            if not state.get("system_prompt"):
                print(
                    "✨ Sistem talimatı durumda bulunamadı. Bu konuşma için ilk kez oluşturuluyor."
                )
                prompt_content = self._create_dynamic_system_prompt()
                # Durumu, oluşturulan talimatla güncellemek için geri döndür.
                return {"system_prompt": prompt_content, "should_end": False}

            # Eğer talimat zaten varsa, hiçbir şey yapma.
            print("✅ Sistem talimatı zaten mevcut. Başlatma adımı atlanıyor.")
            return {}

        def agent_node(state: AgentState):
            """
            Ana aracı düğümü. Artık önceden oluşturulmuş sistem talimatını kullanır.
            """
            # Sistem talimatını durumdan oku
            system_prompt = SystemMessage(content=state["system_prompt"])

            # Mesaj listesini sistem talimatı ile birleştirerek oluştur.
            messages = [system_prompt] + state["messages"]

            # LLM'i çağır.
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        def should_continue(state: AgentState) -> str:
            """
            DÜZELTME: Geliştirilmiş conditional edge logic.
            """
            messages = state["messages"]
            last_message = messages[-1]

            # State-based kontrolü - eğer should_end flag'i set edilmişse END
            if state.get("should_end", False):
                print("🏁 should_end flag is set, ending conversation")
                return END

            # Tool call kontrolü
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                tool_call = last_message.tool_calls[0]
                tool_name = tool_call.get("name", "")

                print(f"🔧 Tool call detected: {tool_name}")

                # Eğer end_conversation tool'u çağrılmışsa, should_end flag'ini set et
                if tool_name == "internal_end_conversation":
                    print("🔚 End conversation tool detected, will end after execution")
                    return "tools"  # Önce tool'u çalıştır, sonra end

                # Diğer tool'lar için normal flow
                return "tools"

            print("💬 No tool calls, continuing conversation")
            return END

        def tools_node_wrapper(state: AgentState):
            """
            Tool node wrapper - end_conversation tool'u çağrıldığında should_end flag'ini set eder.
            Ayrıca tool çıktılarının LLM tarafından doğal dilde işlenmesini sağlar.
            """
            messages = state["messages"]
            last_message = messages[-1]

            # Tool'u çalıştır
            tool_node = ToolNode([self.promo_tool, self.end_conversation_tool])
            result = tool_node.invoke(state)

            # Eğer end_conversation tool'u çağrıldıysa, should_end flag'ini set et
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                tool_call = last_message.tool_calls[0]
                if tool_call.get("name") == "internal_end_conversation":
                    print("🏁 Setting should_end flag to true")
                    result["should_end"] = True

            return result

        # Grafiği YENİ AgentState ile oluştur.
        workflow = StateGraph(AgentState)

        # Düğümlerimizi grafa ekliyoruz.
        workflow.add_node("initializer", initialize_prompt_node)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tools_node_wrapper)

        # Grafiğin GİRİŞ NOKTASINI 'initializer' olarak ayarlıyoruz.
        workflow.set_entry_point("initializer")

        # Düğümler arası akışı (kenarları) tanımlıyoruz.
        # Başlatıcıdan sonra her zaman 'agent' düğümüne git.
        workflow.add_edge("initializer", "agent")

        # 'agent' düğümünden sonra koşullu olarak ya araçlara ya da sona git.
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {"tools": "tools", END: END},
        )

        # 'tools' düğümünden sonra tekrar condition check
        workflow.add_conditional_edges(
            "tools",
            should_continue,
            {
                "tools": "agent",
                END: END,
            },  # should_end flag varsa END, yoksa agent'a dön
        )

        # Derlenmiş grafiği döndür.
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
            # Fallback to static message - handle both nested and flat structures
            business_info = self.call_config.get("business_info", {})
            business_name = (
                business_info.get("company_name")
                or self.call_config.get("business_name")
                or "our company"
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

            language = self.call_config.get("language", "en-US")
            call = self.twilio_client.calls.create(
                to=to_number,
                from_=self.twilio_phone,
                url=webhook_url,
                method="POST",
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

    def process_conversation(
        self, user_input: str, phone_number: str
    ) -> Dict[str, Any]:
        """
        Process user input and get a response from the agent.
        Bu düzeltilmiş versiyonda LangGraph'ın kendi conditional edge logic'i
        conversation'ın bitip bitmeyeceğini belirler.
        """
        thread_id = f"call_{phone_number.strip().replace('+', '')}"
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # 1. Kullanıcının girdisini LangGraph'a gönder ve response al
            response = self.graph.invoke(
                {"messages": [HumanMessage(content=user_input)]}, config=config
            )

            # 2. Response'tan son mesajı ve state'i al
            last_message = response["messages"][-1]
            should_end = response.get("should_end", False)

            print(f"🤖 Agent response: '{last_message.content}'")
            print(f"🏁 Should end: {should_end}")

            # 3. Response'u hazırla
            result = {"text": last_message.content, "should_end": should_end}

            # Tool çağrısı varsa log et
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                tool_name = last_message.tool_calls[0].get("name", "")
                result["tool_called"] = tool_name
                print(f"🔧 Tool called: {tool_name}")
            else:
                result["tool_called"] = None

            return result

        except Exception as e:
            print(f"❌ Conversation error: {str(e)}")
            # Hata durumunda güvenli bir şekilde sonlandır
            return {
                "text": "Sorry, something went wrong. Goodbye.",
                "should_end": True,
                "tool_called": "error_end_conversation",
            }

    def generate_voice_response(
        self, text: str, is_final: bool = False, gather_input: bool = True
    ) -> VoiceResponse:
        """Generate Twilio VoiceResponse with appropriate TTS"""
        response = VoiceResponse()

        # Check if using ElevenLabs or custom TTS
        if isinstance(self.voice_service.tts_provider, ElevenLabsTTS):
            try:
                # Generate audio URL with ElevenLabs (including dynamic voice_id)
                voice_kwargs = {}
                if self.call_config and "selected_voice_id" in self.call_config:
                    voice_kwargs["voice_id"] = self.call_config["selected_voice_id"]
                    print(
                        f"🎤 Using dynamic voice: {self.call_config['selected_voice_id']}"
                    )
                elif self.call_config and "voice_id" in self.call_config:
                    voice_kwargs["voice_id"] = self.call_config["voice_id"]
                    print(f"🎤 Using configured voice: {self.call_config['voice_id']}")

                audio_url = self.voice_service.text_to_speech(text, **voice_kwargs)
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
