import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import Response
from agents.ecommerce.agent import EcommerceAgent
from core.base_agent import AgentState
from core.state_manager import StateManager
from services.twilio_service import TwilioService
from langchain_core.messages import HumanMessage
from utils.logger import get_logger

app = FastAPI(title="LangGraph AI Agents", version="1.0.0")
logger = get_logger(__name__)

# Services
state_manager = StateManager()
twilio_service = TwilioService()

# Agents
ecommerce_agent = EcommerceAgent()

@app.on_event("startup")
async def startup_event():
    """Uygulama başlatılırken agent'ları initialize et"""
    logger.info("Initializing agents...")
    ecommerce_agent.initialize()
    logger.info("All agents initialized successfully")

@app.post("/webhook/twilio/voice")
async def handle_voice_call(request: Request):
    """Telefon araması webhook'u"""
    form_data = await request.form()
    caller_number = form_data.get("From")
    
    logger.info(f"Incoming call from: {caller_number}")
    
    # TwiML yanıtı oluştur
    twiml_response = twilio_service.create_twiml_response(
        "Merhaba! Size nasıl yardımcı olabilirim? Sipariş numaranızı söyleyebilir misiniz?"
    )
    
    return Response(content=twiml_response, media_type="application/xml")

@app.post("/webhook/twilio/sms")
async def handle_sms(request: Request):
    """SMS webhook'u"""
    form_data = await request.form()
    from_number = form_data.get("From")
    message_body = form_data.get("Body")
    
    logger.info(f"SMS from {from_number}: {message_body}")
    
    # E-commerce agent'ını çalıştır
    initial_state = AgentState(
        messages=[HumanMessage(content=message_body)],
        context={
            "phone_number": from_number,
            "order_id": extract_order_id(message_body)
        }
    )
    
    result = await ecommerce_agent.run(initial_state)
    
    return {"status": "processed"}

def extract_order_id(message: str) -> str:
    """Mesajdan order ID'yi çıkar (basit implementation)"""
    import re
    # Basit regex ile order ID bulma
    order_pattern = r'(?:order|sipariş|siparis)[\s\-\:]?(\w+)'
    match = re.search(order_pattern, message.lower())
    return match.group(1) if match else None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agents": ["ecommerce"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)