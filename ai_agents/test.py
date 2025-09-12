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

# Flask için
from flask import Flask, request
import json
import time

# Environment
from dotenv import load_dotenv

load_dotenv()

# Global Twilio client for the tool function
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"), 
    os.getenv("TWILIO_AUTH_TOKEN")
)
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

def send_promo_sms_global(phone_number: str, promo_data: Dict[str, Any]):
    """Global function to send promo SMS that can be called from the tool."""
    try:
        message_body = f"""🎉 Size özel promosyon kodunuz hazır!
Kod: {promo_data['promo_code']}
İndirim: %{promo_data['discount_percent']}
Geçerlilik: {promo_data['valid_until']}
İyi alışverişler dileriz! 🛍️"""
        
        message = twilio_client.messages.create(
            body=message_body, 
            from_=twilio_phone, 
            to=phone_number
        )
        print(f"📱 SMS gönderildi: {phone_number} (SID: {message.sid})")
        return True
    except Exception as e:
        print(f"❌ SMS gönderme hatası: {str(e)}")
        return False

# --- Araç (Tool) Tanımı ---
@tool
def generate_promo_code(
    order_id: str = "", 
    customer_type: str = "regular",
    phone_number: str = ""
) -> Dict[str, Any]:
    """
    Müşteri için bir promosyon kodu oluşturur ve otomatik olarak SMS gönderir.

    Args:
        order_id: Müşterinin sipariş numarası (opsiyonel).
        customer_type: Müşteri tipi (regular, vip, new).
        phone_number: SMS gönderilecek telefon numarası.

    Returns:
        Oluşturulan promosyon kodu bilgilerini içeren bir sözlük.
    """
    print(f"🛠️ generate_promo_code aracı çağrıldı. Müşteri tipi: {customer_type}")
    
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

    # Otomatik SMS gönderimi
    if phone_number:
        sms_sent = send_promo_sms_global(phone_number, promo_data)
        promo_data["sms_sent"] = sms_sent
        print(f"✅ Promosyon kodu oluşturuldu ve SMS gönderildi: {promo_code} (%{discount} indirim)")
    else:
        promo_data["sms_sent"] = False
        print(f"⚠️ Promosyon kodu oluşturuldu ancak telefon numarası eksik: {promo_code} (%{discount} indirim)")

    return promo_data


# --- Ana Agent Sınıfı ---
class TwilioOutboundAgent:
    def __init__(self):
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

        # LLM'i araçlarla kullanılacak şekilde yapılandır
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
        """LangGraph iş akışını oluşturur."""

        def agent_node(state: MessagesState):
            """Müşteri ile konuşan ve araçları çağıran ana düğüm."""
            system_prompt = SystemMessage(
                content="""
            Sen profesyonel ve samimi bir müşteri hizmetleri temsilcisisin. Görevin:
            1. Müşteriyi kibarca karşıla ve özel bir promosyon kodu teklif et.
            2. Müşteri ilgilenirse, "Harika!" gibi olumlu bir yanıt ver ve hemen `generate_promo_code` aracını çağır. 
            3. Araç çağırırken mutlaka phone_number parametresini geçir.
            4. Araç çalıştıktan sonra, "Promosyon kodunuzu ve detayları size SMS olarak gönderiyorum. İyi günler dilerim!" diyerek konuşmayı sonlandır.
            Her zaman Türkçe konuş. Kısa ve net ol.
            """
            )
            # Sistem mesajını sadece konuşmanın başında ekle
            if len(state["messages"]) <= 1:
                messages = [system_prompt] + state["messages"]
            else:
                messages = state["messages"]

            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        # Araçları çalıştıran düğüm
        tool_node = ToolNode([generate_promo_code])

        # İş akışını tanımla
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)

        workflow.set_entry_point("agent")

        # Koşullu kenar: Agent bir araç çağırmaya karar verirse 'tools' düğümüne git,
        # aksi takdirde konuşmayı bitir.
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {"tools": "tools", END: END},
        )
        # Araç çalıştıktan sonra tekrar agent'a dönerek son mesajı oluştur.
        workflow.add_edge("tools", "agent")

        return workflow.compile(checkpointer=self.memory)

    def make_outbound_call(
        self, to_number: str, customer_name: str = ""
    ) -> Dict[str, Any]:
        """Giden bir arama yapar."""
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
            print(f"✅ Giden arama başlatıldı: {to_number} (SID: {call.sid})")
            return {"success": True, "call_sid": call.sid}
        except Exception as e:
            print(f"❌ Arama hatası: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_promo_sms(self, phone_number: str, promo_data: Dict[str, Any]):
        """Promosyon kodunu SMS ile gönderir. (Geriye dönük uyumluluk için)"""
        return send_promo_sms_global(phone_number, promo_data)

    def process_conversation(self, user_input: str, phone_number: str) -> str:
        """
        Kullanıcı girdisini işler ve agent'tan yanıt alır.
        Bu fonksiyon artık senkron çalışır.
        """
        thread_id = f"call_{phone_number.strip().replace('+', '')}"
        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Agent'ı senkron olarak çalıştır
            response = self.graph.invoke(
                {"messages": [HumanMessage(content=user_input)]}, config=config
            )

            # Son mesajı al
            last_message = response["messages"][-1]

            # Eğer son mesaj bir araç çağrısı ise
            if last_message.tool_calls:
                # Araç çağrısına telefon numarasını ekle
                tool_call = last_message.tool_calls[0]
                tool_args = tool_call["args"].copy()
                tool_args["phone_number"] = phone_number
                
                # Aracı çalıştır (SMS otomatik olarak gönderilecek)
                tool_output = generate_promo_code.invoke(tool_args)

                # Agent'ın son cümleyi kurması için süreci devam ettir
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

            # Eğer normal bir AI mesajı ise, içeriğini döndür
            return last_message.content

        except Exception as e:
            print(f"❌ Konuşma hatası: {str(e)}")
            return "Üzgünüm, bir sorun oluştu. İyi günler dilerim."


# --- Flask Webhook Sunucusu ---
def create_webhook_server():
    """Twilio webhook'ları için Flask sunucusunu oluşturur."""
    app = Flask(__name__)
    # Agent'ı uygulama başlatıldığında bir kez oluştur
    agent = TwilioOutboundAgent()

    @app.route("/webhook/outbound/start", methods=["POST"])
    def handle_outbound_start():
        """Giden arama başladığında çalışır ve ilk mesajı okur."""
        print("📞 Gelen Webhook isteği: /webhook/outbound/start")
        response = VoiceResponse()
        gather = response.gather(
            input="speech",
            action="/webhook/outbound/process",
            method="POST",
            speech_timeout="auto",
            language="tr-TR",
        )
        gather.say(
            "Merhaba, size özel bir promosyon kodu teklifi için arıyorum. İlgilenir misiniz?",
            voice="Polly.Filiz",
            language="tr-TR",
        )
        response.say(
            "Yanıt alamadım. İyi günler dilerim.",
            voice="Polly.Filiz",
            language="tr-TR",
        )
        response.hangup()
        return str(response)

    @app.route("/webhook/outbound/process", methods=["POST"])
    def handle_outbound_process():
        """Kullanıcının konuşmasını işler."""
        call_sid = request.form.get("CallSid")
        to_number = request.form.get("To")
        speech_result = request.form.get("SpeechResult", "")

        print(f"🎤 Kullanıcıdan gelen sesli yanıt ({to_number}): '{speech_result}'")

        # Agent'tan yanıtı al (artık senkron)
        agent_response_text = agent.process_conversation(speech_result, to_number)

        response = VoiceResponse()

        # Eğer agent sonlandırma mesajı verdiyse, telefonu kapat
        if (
            "sms" in agent_response_text.lower()
            or "gönderiyorum" in agent_response_text.lower()
        ):
            response.say(agent_response_text, voice="Polly.Filiz", language="tr-TR")
            response.hangup()
        else:
            # Konuşma devam ediyorsa, tekrar dinle
            gather = response.gather(
                input="speech",
                action="/webhook/outbound/process",
                method="POST",
                speech_timeout="auto",
                language="tr-TR",
            )
            gather.say(agent_response_text, voice="Polly.Filiz", language="tr-TR")
            response.say(
                "Yanıtınızı alamadım. İyi günler.",
                voice="Polly.Filiz",
                language="tr-TR",
            )
            response.hangup()

        return str(response)

    # Test ve yönetim endpoint'leri
    @app.route("/make-call", methods=["POST"])
    def make_call_endpoint():
        data = request.get_json()
        phone_number = data.get("phone_number")
        if not phone_number:
            return {"error": "phone_number gerekli"}, 400
        result = agent.make_outbound_call(phone_number)
        return result

    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "healthy"}

    return app


# --- Uygulama Başlatma ---
if __name__ == "__main__":
    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "GOOGLE_API_KEY",
        "WEBHOOK_BASE_URL",
    ]
    if any(not os.getenv(var) for var in required_vars):
        print(f"❌ Eksik ortam değişkenleri. Lütfen .env dosyanızı kontrol edin.")
        exit(1)

    print("🤖 Twilio Outbound AI Agent")
    print("1. Webhook sunucusunu başlat")
    print("2. Test araması yap")
    choice = input("Seçiminiz (1-2): ").strip()

    if choice == "1":
        print("🚀 Webhook sunucusu http://0.0.0.0:5000 adresinde başlatılıyor...")
        app = create_webhook_server()
        # debug=False production ortamı için daha uygundur.
        app.run(host="0.0.0.0", port=5000, debug=False)
    elif choice == "2":
        agent = TwilioOutboundAgent()
        test_phone = input(
            "Test için telefon numaranızı girin (+90xxxxxxxxxx): "
        ).strip()
        if test_phone:
            agent.make_outbound_call(test_phone)
        else:
            print("❌ Geçerli bir telefon numarası girmediniz.")
    else:
        print("❌ Geçersiz seçim.")