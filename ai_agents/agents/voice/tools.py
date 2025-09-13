"""
Voice agent tools for promo code generation and SMS sending
"""

import os
import random
import string
from typing import Dict, Any
from datetime import datetime

from langchain_core.tools import tool
from twilio.rest import Client


# Initialize Twilio client
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")


def send_promo_sms_global(phone_number: str, promo_data: Dict[str, Any]) -> bool:
    """Global function to send promo SMS"""
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


@tool
def generate_promo_code(
    order_id: str = "",
    customer_type: str = "regular",
    phone_number: str = "+31687611451",  # Should be dynamic in real implementation
) -> Dict[str, Any]:
    """Generate a promo code for the customer and automatically send it via SMS."""
    print(f"🛠️ generate_promo_code tool called. Customer type: {customer_type}")

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
