import os
import asyncio
import random
import string
from typing import Dict, Any, List, Optional
from datetime import datetime

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Twilio imports
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse

# Flask
from flask import Flask, request
import json
import time

# Environment
from dotenv import load_dotenv

load_dotenv()

# Global Twilio client for the tool function
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")


def send_promo_sms_global(phone_number: str, promo_data: Dict[str, Any]):
    """Global function to send promo SMS that can be called from the tool."""
    try:
        message_body = f"""🎉 Your exclusive promo code is ready!
Code: {promo_data['promo_code']}
Discount: %{promo_data['discount_percent']}
Valid until: {promo_data['valid_until']}
Happy shopping! 🛍️"""

        message = twilio_client.messages.create(
            body=message_body, from_=twilio_phone, to=phone_number
        )
        print(f"📱 SMS sent: {phone_number} (SID: {message.sid})")
        return True
    except Exception as e:
        print(f"❌ SMS sending error: {str(e)}")
        return False


# --- Tool Definition ---
@tool
def generate_promo_code(
    order_id: str = "",
    customer_type: str = "regular",
) -> Dict[str, Any]:
    """
    Generates a promo code for the customer and automatically sends it via SMS.

    Args:
        order_id: Customer's order ID (optional).
        customer_type: Customer type (regular, vip, new).

    Returns:
        A dictionary containing the generated promo code details.
    """
    print(f"🛠️ generate_promo_code tool called. Customer type: {customer_type}")

    phone_number = "+31687611451"

    if customer_type == "vip":
        discount = random.randint(25, 40)
        prefix = "VIP"
    elif customer_type == "new":
        discount = random.randint(15, 25)
        prefix = "NEW"
    else:
        discount = random.randint(10, 20)
        prefix = "SAVE"

    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    promo_code = f"{prefix}{suffix}"

    promo_data = {
        "promo_code": promo_code,
        "discount_percent": discount,
        "order_id": order_id or "N/A",
        "customer_type": customer_type,
        "valid_until": "2025-12-31",
        "generated_at": datetime.now().isoformat(),
    }

    # Automatic SMS sending
    if phone_number:
        sms_sent = send_promo_sms_global(phone_number, promo_data)
        promo_data["sms_sent"] = sms_sent
        print(
            f"✅ Promo code generated and SMS sent: {promo_code} (%{discount} discount)"
        )
    else:
        promo_data["sms_sent"] = False
        print(
            f"⚠️ Promo code generated but missing phone number: {promo_code} (%{discount} discount)"
        )

    return promo_data


# --- Main Agent Class ---
class TwilioOutboundAgent:
    def __init__(self):
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

        # Configure LLM with tools
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
        self.llm_with_tools = self.llm.bind_tools([generate_promo_code])

        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.active_calls = {}

    def _build_graph(self):
        """Build LangGraph workflow."""

        def agent_node(state: MessagesState):
            """Main node that talks to the customer and calls tools."""
            system_prompt = SystemMessage(
                content="""
            You are a professional and friendly customer service representative. You understand all languages and will continue in whichever language the customer speaks. Your tasks:
            1. Politely greet the customer and offer a special promo code.
            2. If the customer is interested, respond positively (e.g., "Great!") and immediately call the `generate_promo_code` tool. 
            3. Always pass the phone_number parameter when calling the tool.
            4. After the tool runs, say "I am sending your promo code and details via SMS. Have a great day!" and end the conversation.
            """
            )
            # Add system prompt only at the start of the conversation
            if len(state["messages"]) <= 1:
                messages = [system_prompt] + state["messages"]
            else:
                messages = state["messages"]

            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        # Tool execution node
        tool_node = ToolNode([generate_promo_code])

        # Define workflow
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

    def send_promo_sms(self, phone_number: str, promo_data: Dict[str, Any]):
        """Send promo code via SMS (for backward compatibility)."""
        return send_promo_sms_global(phone_number, promo_data)

    def process_conversation(self, user_input: str, phone_number: str) -> str:
        """
        Process user input and get a response from the agent.
        This function now works synchronously.
        """
        thread_id = f"call_{phone_number.strip().replace('+', '')}"
        config = {"configurable": {"thread_id": thread_id}}

        try:
            response = self.graph.invoke(
                {"messages": [HumanMessage(content=user_input)]}, config=config
            )

            last_message = response["messages"][-1]

            if last_message.tool_calls:
                tool_call = last_message.tool_calls[0]
                tool_args = tool_call["args"].copy()
                tool_args["phone_number"] = phone_number

                tool_output = generate_promo_code.invoke(tool_args)

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
            return "Sorry, something went wrong. Goodbye."


# --- Flask Webhook Server ---
def create_webhook_server():
    """Create Flask server for Twilio webhooks."""
    app = Flask(__name__)
    agent = TwilioOutboundAgent()

    @app.route("/webhook/outbound/start", methods=["POST"])
    def handle_outbound_start():
        """Triggered when outbound call starts and plays the first message."""
        print("📞 Incoming Webhook request: /webhook/outbound/start")
        response = VoiceResponse()
        gather = response.gather(
            input="speech",
            action="/webhook/outbound/process",
            method="POST",
            speech_timeout="auto",
            language="en-US",
        )
        gather.say(
            "Hello, I am calling to offer you a special promo code. Are you interested?",
            voice="Polly.Joanna",
            language="en-US",
        )
        response.say(
            "I didn’t get a response. Have a great day.",
            voice="Polly.Joanna",
            language="en-US",
        )
        response.hangup()
        return str(response)

    @app.route("/webhook/outbound/process", methods=["POST"])
    def handle_outbound_process():
        """Process user speech input."""
        call_sid = request.form.get("CallSid")
        to_number = request.form.get("To")
        speech_result = request.form.get("SpeechResult", "")

        print(f"🎤 User response ({to_number}): '{speech_result}'")

        agent_response_text = agent.process_conversation(speech_result, to_number)

        response = VoiceResponse()

        if (
            "sms" in agent_response_text.lower()
            or "sending" in agent_response_text.lower()
        ):
            response.say(agent_response_text, voice="Polly.Joanna", language="en-US")
            response.hangup()
        else:
            gather = response.gather(
                input="speech",
                action="/webhook/outbound/process",
                method="POST",
                speech_timeout="auto",
                language="en-US",
            )
            gather.say(agent_response_text, voice="Polly.Joanna", language="en-US")
            response.say(
                "I didn’t get your response. Goodbye.",
                voice="Polly.Joanna",
                language="en-US",
            )
            response.hangup()

        return str(response)

    @app.route("/make-call", methods=["POST"])
    def make_call_endpoint():
        data = request.get_json()
        phone_number = data.get("phone_number")
        if not phone_number:
            return {"error": "phone_number is required"}, 400
        result = agent.make_outbound_call(phone_number)
        return result

    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "healthy"}

    return app


# --- App Entry Point ---
if __name__ == "__main__":
    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "GOOGLE_API_KEY",
        "WEBHOOK_BASE_URL",
    ]
    if any(not os.getenv(var) for var in required_vars):
        print("❌ Missing environment variables. Please check your .env file.")
        exit(1)

    print("🤖 Twilio Outbound AI Agent")
    print("1. Start webhook server")
    print("2. Make test call")
    choice = input("Your choice (1-2): ").strip()

    if choice == "1":
        print("🚀 Starting webhook server at http://0.0.0.0:5000...")
        app = create_webhook_server()
        app.run(host="0.0.0.0", port=5000, debug=False)
    elif choice == "2":
        agent = TwilioOutboundAgent()
        test_phone = input(
            "Enter your phone number for testing (+1xxxxxxxxxx): "
        ).strip()
        if test_phone:
            agent.make_outbound_call(test_phone)
        else:
            print("❌ Invalid phone number.")
    else:
        print("❌ Invalid choice.")
