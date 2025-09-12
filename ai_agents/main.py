from flask import Flask, request
from twilio.rest import Client
from twilio.twiml import VoiceResponse, MessagingResponse
from agents.ecommerce_agent import EcommerceAgent
from config.settings import settings
from utils.logger import get_logger
import asyncio
import os

app = Flask(__name__)
logger = get_logger(__name__)

# Twilio Client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# E-commerce Agent
ecommerce_agent = EcommerceAgent()
ecommerce_agent.initialize()


def run_async_in_thread(coro):
    """Async fonksiyonları Flask context'inde çalıştır"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        logger.error(f"Async execution error: {str(e)}")
        return None
    finally:
        loop.close()


@app.route("/webhook/voice/incoming", methods=["POST"])
def handle_incoming_call():
    """
    Gelen telefon aramasını karşılar
    Twilio otomatik olarak bu endpoint'i çağırır
    """
    # Twilio'dan gelen veriler
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    call_sid = request.form.get("CallSid")
    call_status = request.form.get("CallStatus")

    logger.info(f"📞 Incoming call: {from_number} -> {to_number} (SID: {call_sid})")

    # TwiML Response oluştur
    response = VoiceResponse()

    # Karşılama mesajı
    welcome_message = """Merhaba! Size yardımcı olmak için buradayım. 
    Promo kod almak için 'promo kod istiyorum' deyin veya 1'e basın.
    Sipariş numaranız varsa söyleyebilirsiniz."""

    # Gather ile kullanıcı input'u topla
    gather = response.gather(
        input="speech dtmf",
        action="/webhook/voice/process",
        method="POST",
        speechTimeout="auto",
        language="tr-TR",
        num_digits=1,
    )

    # Mesajı söyle
    gather.say(welcome_message, voice="Polly.Filiz", language="tr-TR")  # Türkçe ses

    # Timeout durumu için fallback
    response.say(
        "Bir yanıt alamadım. Promo kodunuz SMS olarak gönderilecek.",
        voice="Polly.Filiz",
        language="tr-TR",
    )

    # Timeout durumunda da promo kod gönder
    response.redirect("/webhook/voice/timeout?From=" + from_number)

    return str(response), 200, {"Content-Type": "application/xml"}


@app.route("/webhook/voice/process", methods=["POST"])
def process_voice_input():
    """
    Kullanıcının sesli veya DTMF input'unu işler
    """
    # Twilio'dan gelen veriler
    from_number = request.form.get("From")
    speech_result = request.form.get("SpeechResult", "")
    digits = request.form.get("Digits", "")
    confidence = request.form.get("Confidence", "0")

    # Input'u belirle
    user_input = speech_result.strip() if speech_result else digits

    logger.info(
        f"🗣️ Voice input from {from_number}: '{user_input}' (confidence: {confidence})"
    )

    # TwiML Response
    response = VoiceResponse()

    try:
        # Agent ile kullanıcı input'unu işle
        agent_result = run_async_in_thread(
            ecommerce_agent.process_call(from_number, user_input)
        )

        if agent_result and agent_result.context.get("sms_sent", False):
            # Başarılı promo kod gönderimi
            success_message = "Harika! Promo kodunuz SMS olarak telefon numaranıza gönderilmiştir. Mesajlarınızı kontrol edebilirsiniz. İyi alışverişler!"

            response.say(success_message, voice="Polly.Filiz", language="tr-TR")

        elif user_input == "1" or "promo" in user_input.lower():
            # Kullanıcı promo kod istiyor
            processing_message = "Promo kodunuz hazırlanıyor ve SMS olarak gönderilecek. Lütfen bekleyin..."
            response.say(processing_message, voice="Polly.Filiz", language="tr-TR")

            # Arka planda promo kod oluştur ve gönder
            generate_and_send_promo(from_number)

            # Son mesaj
            final_message = "Promo kodunuz gönderilmiştir. Teşekkürler!"
            response.say(final_message, voice="Polly.Filiz", language="tr-TR")

        else:
            # Belirsiz input
            clarify_message = "Promo kod almak için 1'e basabilir veya 'promo kod istiyorum' diyebilirsiniz."
            response.say(clarify_message, voice="Polly.Filiz", language="tr-TR")

            # Tekrar input iste
            response.redirect("/webhook/voice/incoming")

    except Exception as e:
        logger.error(f"❌ Voice processing error: {str(e)}")
        error_message = "Üzgünüm, bir teknik sorun yaşıyoruz. Promo kodunuz SMS olarak gönderilecek."
        response.say(error_message, voice="Polly.Filiz", language="tr-TR")

        # Hata durumunda da promo kod gönder
        generate_and_send_promo(from_number)

    # Aramayı bitir
    response.hangup()

    return str(response), 200, {"Content-Type": "application/xml"}


@app.route("/webhook/voice/timeout", methods=["GET", "POST"])
def handle_voice_timeout():
    """
    Kullanıcı yanıt vermediğinde çalışır
    """
    from_number = request.args.get("From") or request.form.get("From")

    logger.info(f"⏱️ Voice timeout for {from_number}")

    # Timeout durumunda promo kod gönder
    generate_and_send_promo(from_number)

    response = VoiceResponse()
    response.say(
        "Promo kodunuz SMS olarak gönderildi. İyi günler!",
        voice="Polly.Filiz",
        language="tr-TR",
    )
    response.hangup()

    return str(response), 200, {"Content-Type": "application/xml"}


def generate_and_send_promo(phone_number: str, order_id: str = None):
    """
    Promo kodu oluştur ve SMS ile gönder
    """
    try:
        from services.promo_service import generate_promo_code_tool

        # Promo kod oluştur
        promo_result = generate_promo_code_tool.invoke({"order_id": order_id or ""})

        # SMS mesajı hazırla
        sms_message = f"""🎉 İşte Promo Kodunuz!

Kod: {promo_result['promo_code']}
İndirim: %{promo_result['discount_percent']}

Bu kodu siparişinizde kullanabilirsiniz.
İyi alışverişler! 🛍️"""

        # SMS gönder
        message = twilio_client.messages.create(
            body=sms_message, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number
        )

        logger.info(f"📱 SMS sent to {phone_number}: {message.sid}")
        return True

    except Exception as e:
        logger.error(f"❌ SMS send error for {phone_number}: {str(e)}")
        return False


@app.route("/webhook/sms", methods=["POST"])
def handle_sms():
    """
    Gelen SMS'leri işler (opsiyonel)
    """
    from_number = request.form.get("From")
    message_body = request.form.get("Body", "").strip()

    logger.info(f"💬 SMS from {from_number}: {message_body}")

    response = MessagingResponse()

    try:
        # SMS ile promo kod talebi
        if any(
            word in message_body.lower()
            for word in ["promo", "kod", "indirim", "kampanya"]
        ):
            # Promo kod oluştur ve gönder
            success = generate_and_send_promo(from_number)

            if success:
                response.message("✅ Promo kodunuz gönderildi!")
            else:
                response.message(
                    "❌ Promo kod gönderilirken hata oluştu. Lütfen tekrar deneyin."
                )
        else:
            response.message(
                "Promo kod için 'promo kod' yazabilirsiniz veya bizi arayabilirsiniz."
            )

    except Exception as e:
        logger.error(f"❌ SMS processing error: {str(e)}")
        response.message("Bir hata oluştu. Lütfen tekrar deneyin.")

    return str(response), 200, {"Content-Type": "application/xml"}


@app.route("/make-call", methods=["POST"])
def make_outbound_call():
    """
    Giden arama yapma endpoint'i (test/marketing için)
    """
    data = request.get_json()
    to_number = data.get("to_number")

    if not to_number:
        return {"error": "Phone number required"}, 400

    try:
        # TwiML URL - bu callback URL olarak kullanılır
        twiml_url = request.url_root.rstrip("/") + "/webhook/voice/outbound"

        # Twilio ile arama yap
        call = twilio_client.calls.create(
            to=to_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=twiml_url,
            method="POST",
        )

        logger.info(f"📞 Outbound call initiated to {to_number}: {call.sid}")

        return {"status": "success", "call_sid": call.sid, "to": to_number}, 200

    except Exception as e:
        logger.error(f"❌ Outbound call error: {str(e)}")
        return {"error": str(e)}, 500


@app.route("/webhook/voice/outbound", methods=["POST"])
def handle_outbound_call():
    """
    Giden aramaları işler (marketing/promo çağrıları için)
    """
    to_number = request.form.get("To")
    call_status = request.form.get("CallStatus")

    logger.info(f"📞 Outbound call to {to_number}, status: {call_status}")

    response = VoiceResponse()

    if call_status == "completed":
        # Arama bağlandı
        message = """Merhaba! Size özel bir promo kod teklifi var. 
        Bu çağrı otomatik olarak sonlandırılacak ve promo kodunuz SMS ile gönderilecek. 
        Teşekkürler!"""

        response.say(message, voice="Polly.Filiz", language="tr-TR")

        # Promo kod gönder
        generate_and_send_promo(to_number)

    return str(response), 200, {"Content-Type": "application/xml"}


@app.route("/health", methods=["GET"])
def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "agent": "ecommerce",
        "twilio": "connected",
        "version": "1.0.0",
    }


@app.route("/test/promo/<phone_number>", methods=["GET"])
def test_promo_send(phone_number):
    """Test endpoint - Promo kod göndermeyi test et"""
    success = generate_and_send_promo(phone_number)

    return {
        "status": "success" if success else "failed",
        "phone_number": phone_number,
        "message": "Promo code sent" if success else "Failed to send",
    }


@app.route("/webhook/call-status", methods=["POST"])
def call_status_callback():
    """
    Arama durumu callback'i (opsiyonel - monitoring için)
    """
    call_sid = request.form.get("CallSid")
    call_status = request.form.get("CallStatus")
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    duration = request.form.get("CallDuration", "0")

    logger.info(
        f"📊 Call status update: {call_sid} - {call_status} - Duration: {duration}s"
    )

    # Burada call analytics, billing vs. yapılabilir

    return "OK", 200


if __name__ == "__main__":
    logger.info(f"🚀 Starting Twilio AI Agent Server on port {settings.FLASK_PORT}")
    logger.info(f"📞 Twilio Phone: {settings.TWILIO_PHONE_NUMBER}")

    app.run(
        host="0.0.0.0",
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG,
        threaded=True,  # Multi-threading için
    )
