import random
import string
from typing import Dict, Any
from langchain_core.tools import tool


class PromoCodeService:
    @staticmethod
    def generate_promo_code(order_id: str = None) -> str:
        """Promo kodu oluşturur"""
        if order_id:
            # Order ID bazlı promo kod
            prefix = order_id[:4].upper() if len(order_id) >= 4 else order_id.upper()
            suffix = "".join(random.choices(string.digits, k=4))
            return f"PROMO{prefix}{suffix}"
        else:
            # Genel promo kod
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            return f"PROMO{code}"

    @staticmethod
    def get_discount_amount() -> int:
        """İndirim miktarını döner"""
        return random.choice([10, 15, 20, 25, 30])


# LangGraph tool olarak tanımla
@tool
def generate_promo_code_tool(order_id: str = "") -> Dict[str, Any]:
    """
    Müşteri için promo kodu oluşturur.

    Args:
        order_id: Opsiyonel sipariş numarası

    Returns:
        Promo kodu ve detayları içeren dict
    """
    promo_service = PromoCodeService()
    promo_code = promo_service.generate_promo_code(order_id)
    discount = promo_service.get_discount_amount()

    return {
        "promo_code": promo_code,
        "discount_percent": discount,
        "order_id": order_id or "N/A",
        "status": "generated",
    }
