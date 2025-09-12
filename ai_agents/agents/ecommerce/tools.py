import random
import string
from langchain_core.tools import tool
from typing import Dict, Any

@tool
async def get_promo_code_tool(order_id: str) -> Dict[str, Any]:
    """
    Order ID'ye göre promo kodu oluşturur.
    
    Args:
        order_id: Sipariş numarası
        
    Returns:
        Dict containing promo code and details
    """
    # Basit promo kodu oluştur
    promo_code = "PROMO" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    return {
        "order_id": order_id,
        "promo_code": promo_code,
        "discount_percent": random.randint(10, 30),
        "valid_until": "2024-12-31",
        "status": "active"
    }

@tool
async def validate_order_tool(order_id: str) -> Dict[str, Any]:
    """
    Order ID'nin geçerliliğini kontrol eder.
    
    Args:
        order_id: Sipariş numarası
        
    Returns:
        Dict containing validation result
    """
    # Basit validasyon (gerçek uygulamada database'den kontrol edilir)
    is_valid = len(order_id) >= 5 and order_id.isalnum()
    
    return {
        "order_id": order_id,
        "is_valid": is_valid,
        "exists": is_valid,
        "status": "completed" if is_valid else "not_found"
    }