from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_services():
    """Get services (placeholder)."""
    return {"services": [{"name": "car_rental"}, {"name": "restaurant"}, {"name": "shopify"}], "total": 3}