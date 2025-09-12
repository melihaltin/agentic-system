from twilio.rest import Client
from twilio.twiml import VoiceResponse, MessagingResponse
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER

    def make_promo_call(self, to_number: str, callback_url: str = None) -> str:
        """
        Promo kod için giden arama yapar

        Args:
            to_number: Aranacak numara
            callback_url: TwiML callback URL

        Returns:
            Call SID
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=callback_url or f"{settings.BASE_URL}/webhook/voice/outbound",
                method="POST",
                status_callback=f"{settings.BASE_URL}/webhook/call-status",
                status_callback_method="POST",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
            )

            logger.info(f"📞 Promo call initiated: {call.sid}")
            return call.sid

        except Exception as e:
            logger.error(f"❌ Call initiation failed: {str(e)}")
            raise

    def send_promo_sms(self, to_number: str, promo_code: str, discount: int) -> bool:
        """
        Promo kod SMS'i gönder

        Args:
            to_number: SMS gönderilecek numara
            promo_code: Promo kodu
            discount: İndirim yüzdesi

        Returns:
            Success status
        """
        try:
            message_body = f"""🎉 Özel Promo Kodunuz!

💰 Kod: {promo_code}
📊 İndirim: %{discount}

✅ Siparişinizde bu kodu kullanın
⏰ Sınırlı süre geçerli

İyi alışverişler! 🛍️"""

            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=to_number,
                status_callback=f"{settings.BASE_URL}/webhook/sms-status",
            )

            logger.info(f"📱 Promo SMS sent: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"❌ SMS send failed: {str(e)}")
            return False

    def create_interactive_voice_response(
        self, message: str, options: dict = None
    ) -> str:
        """
        İnteraktif sesli yanıt oluştur

        Args:
            message: Okunacak mesaj
            options: DTMF seçenekleri

        Returns:
            TwiML string
        """
        response = VoiceResponse()

        if options:
            gather = response.gather(
                input="dtmf speech",
                action="/webhook/voice/process",
                method="POST",
                num_digits=1,
                speech_timeout="auto",
                language="tr-TR",
            )

            # Ana mesaj
            gather.say(message, voice="Polly.Filiz", language="tr-TR")

            # Seçenekleri oku
            for key, value in options.items():
                gather.say(f"{key} için {value}", voice="Polly.Filiz", language="tr-TR")

            # Timeout fallback
            response.say(
                "Bir seçim yapmadınız. Promo kodunuz SMS olarak gönderilecek.",
                voice="Polly.Filiz",
                language="tr-TR",
            )
        else:
            response.say(message, voice="Polly.Filiz", language="tr-TR")

        return str(response)
