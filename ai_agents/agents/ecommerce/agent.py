from typing import Dict, Any, List
from langgraph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core.base_agent import BaseAgent, AgentState
from services.promo_service import generate_promo_code_tool
from services.twilio_service import TwilioService
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class EcommerceAgent(BaseAgent):
    def __init__(self):
        super().__init__("ecommerce_support")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.1, api_key=settings.OPENAI_API_KEY
        )
        self.twilio_service = TwilioService()

    def define_tools(self):
        """E-commerce agent'ının kullanacağı tool'ları tanımlar"""
        return [generate_promo_code_tool]

    def build_workflow(self) -> StateGraph:
        """E-commerce agent workflow'unu oluşturur"""
        workflow = StateGraph(AgentState)

        # Nodes
        workflow.add_node("greeting", self.greeting_node)
        workflow.add_node("process_request", self.process_request_node)
        workflow.add_node("generate_promo", self.generate_promo_node)
        workflow.add_node("send_sms", self.send_sms_node)
        workflow.add_node("final_response", self.final_response_node)

        # Entry point
        workflow.set_entry_point("greeting")

        # Conditional edges
        workflow.add_conditional_edges(
            "greeting",
            self.should_continue_after_greeting,
            {"process": "process_request", "end": "final_response"},
        )

        workflow.add_edge("process_request", "generate_promo")
        workflow.add_edge("generate_promo", "send_sms")
        workflow.add_edge("send_sms", "final_response")
        workflow.add_edge("final_response", END)

        return workflow.compile()

    async def greeting_node(self, state: AgentState) -> AgentState:
        """Karşılama mesajı"""
        greeting_msg = """Merhaba! Size nasıl yardımcı olabilirim? 
        
Promo kod almak için:
- 'Promo kod istiyorum' diyebilirsiniz
- Sipariş numaranız varsa söyleyebilirsiniz

Size nasıl yardımcı olabilirim?"""

        state.context["greeting_done"] = True
        state.context["voice_response"] = greeting_msg

        logger.info(f"Greeting sent to {state.phone_number}")
        return state

    async def process_request_node(self, state: AgentState) -> AgentState:
        """Kullanıcı talebini işler"""
        user_message = ""
        if state.messages:
            user_message = state.messages[-1].content

        # LLM ile kullanıcı niyetini analiz et
        system_msg = SystemMessage(
            content="""
        Sen bir e-ticaret müşteri hizmetleri asistanısın. 
        Kullanıcının promo kod isteyip istemediğini anla.
        Eğer promo kod istiyorsa, sipariş numarası var mı kontrol et.
        
        Yanıtın şu formatda olsun:
        {
            "wants_promo": true/false,
            "order_id": "sipariş numarası veya boş",
            "action": "generate_promo" veya "clarify"
        }
        """
        )

        messages = [system_msg, HumanMessage(content=user_message)]
        response = await self.llm.ainvoke(messages)

        # Response'u parse et (basitleştirilmiş)
        content = response.content.lower()
        wants_promo = "promo" in content or "kod" in content or "indirim" in content

        state.context["wants_promo"] = wants_promo
        state.context["user_input"] = user_message

        logger.info(
            f"Processed request from {state.phone_number}: wants_promo={wants_promo}"
        )
        return state

    async def generate_promo_node(self, state: AgentState) -> AgentState:
        """Promo kodu oluşturur"""
        order_id = state.context.get("order_id", "")

        # Tool'u çağır
        promo_result = await generate_promo_code_tool.ainvoke({"order_id": order_id})

        state.context["promo_data"] = promo_result

        logger.info(
            f"Generated promo code for {state.phone_number}: {promo_result['promo_code']}"
        )
        return state

    async def send_sms_node(self, state: AgentState) -> AgentState:
        """SMS gönderir"""
        promo_data = state.context.get("promo_data", {})

        if promo_data:
            sms_message = f"""🎉 Promo Kodunuz Hazır!

Kod: {promo_data['promo_code']}
İndirim: %{promo_data['discount_percent']}

Bu kodu sipariş verirken kullanabilirsiniz. İyi alışverişler!"""

            success = self.twilio_service.send_sms(state.phone_number, sms_message)
            state.context["sms_sent"] = success

        logger.info(
            f"SMS sent to {state.phone_number}: {state.context.get('sms_sent', False)}"
        )
        return state

    async def final_response_node(self, state: AgentState) -> AgentState:
        """Son yanıt"""
        if state.context.get("sms_sent", False):
            response_msg = "Harika! Promo kodunuz SMS olarak gönderilmiştir. Telefonunuzu kontrol edebilirsiniz. İyi günler!"
        else:
            response_msg = "Üzgünüm, promo kod oluştururken bir sorun yaşandı. Lütfen daha sonra tekrar deneyin."

        state.context["final_response"] = response_msg
        state.completed = True

        # AI mesajını ekle
        state.messages.append(AIMessage(content=response_msg))

        logger.info(f"Final response for {state.phone_number}: {response_msg[:50]}...")
        return state

    def should_continue_after_greeting(self, state: AgentState) -> str:
        """Karşılamadan sonra devam edip etmeyeceğine karar verir"""
        # Eğer kullanıcı input'u varsa işle, yoksa bitir
        if state.messages and len(state.messages) > 0:
            return "process"
        return "end"
