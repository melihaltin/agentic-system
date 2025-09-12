from twilio.rest import Client
from twilio.twiml import TwiML
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number

    async def send_sms(self, to_number: str, message: str) -> bool:
        """SMS gönder"""
        try:
            message = self.client.messages.create(
                body=message, from_=self.phone_number, to=to_number
            )
            logger.info(f"SMS sent successfully: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False

    async def make_call(self, to_number: str, twiml_url: str) -> bool:
        """Telefon araması yap"""
        try:
            call = self.client.calls.create(
                to=to_number, from_=self.phone_number, url=twiml_url
            )
            logger.info(f"Call initiated successfully: {call.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to make call: {str(e)}")
            return False

    def create_twiml_response(self, message: str) -> str:
        """TwiML yanıtı oluştur"""
        response = TwiML()
        response.say(message, voice="alice", language="tr-TR")
        return str(response)
