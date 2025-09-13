from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_businesses():
    """Get businesses (placeholder)."""
    return {"businesses": [], "message": "Businesses API - not implemented yet"}