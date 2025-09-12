from typing import List, Dict, Any
from langgraph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from core.base_agent import BaseAgent, AgentState
from .tools import get_promo_code_tool
from services.twilio_service import TwilioService
from config.settings import settings


class EcommerceAgent(BaseAgent):
    def __init__(self):
        super().__init__("ecommerce_001", "E-commerce Support Agent")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.1, api_key=settings.openai_api_key
        )
        self.twilio_service = TwilioService()

    def define_tools(self) -> List:
        """E-commerce için gerekli tool'ları tanımla"""
        return [get_promo_code_tool]

    def build_graph(self) -> StateGraph:
        """E-commerce agent için graph yapısını oluştur"""
        workflow = StateGraph(AgentState)

        # Nodes
        workflow.add_node("process_request", self.process_request)
        workflow.add_node("generate_promo", self.generate_promo)
        workflow.add_node("send_response", self.send_response)

        # Edges
        workflow.set_entry_point("process_request")
        workflow.add_edge("process_request", "generate_promo")
        workflow.add_edge("generate_promo", "send_response")
        workflow.add_edge("send_response", END)

        return workflow.compile()

    async def process_request(self, state: AgentState) -> AgentState:
        """Müşteri talebini işle"""
        messages = state.messages
        last_message = messages[-1] if messages else None

        if last_message:
            # LLM ile talebi analiz et
            response = await self.llm.ainvoke(
                [
                    HumanMessage(
                        content=f"""
                Müşteri talebini analiz et ve order ID'yi çıkar:
                Müşteri mesajı: {last_message.content}
                
                Eğer order ID varsa çıkar, yoksa müşteriden iste.
                """
                    )
                ]
            )

            state.context["analysis"] = response.content

        return state

    async def generate_promo(self, state: AgentState) -> AgentState:
        """Promo kodu oluştur"""
        # Order ID'yi context'ten al
        order_id = state.context.get("order_id")

        if order_id:
            # Promo kodu tool'unu kullan
            promo_result = await get_promo_code_tool.ainvoke({"order_id": order_id})
            state.context["promo_code"] = promo_result["promo_code"]
            state.context["message"] = (
                f"Siparişiniz için promo kodunuz: {promo_result['promo_code']}"
            )
        else:
            state.context["message"] = (
                "Promo kodu oluşturmak için lütfen sipariş numaranızı paylaşın."
            )

        return state

    async def send_response(self, state: AgentState) -> AgentState:
        """Yanıtı gönder"""
        message = state.context.get("message", "Bir hata oluştu.")
        phone_number = state.context.get("phone_number")

        if phone_number:
            # Twilio ile SMS gönder
            await self.twilio_service.send_sms(phone_number, message)

        state.messages.append(AIMessage(content=message))
        state.completed = True

        return state
