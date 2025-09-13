"""
Twilio Outbound Voice Agent
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
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Twilio imports
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from services.voice_service import VoiceService
from services.tts.elevenlabs import ElevenLabsTTS
from agents.voice.tools import generate_promo_code


class TwilioOutboundAgent:
    """Twilio outbound voice agent with LangGraph integration"""

    def __init__(self, voice_service: VoiceService):
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        self.voice_service = voice_service

        # Configure LLM with tools
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
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

            if len(state["messages"]) <= 1:
                messages = [system_prompt] + state["messages"]
            else:
                messages = state["messages"]

            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        tool_node = ToolNode([generate_promo_code])

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

    def generate_voice_response(
        self, text: str, is_final: bool = False
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

        if is_final:
            response.hangup()

        return response
