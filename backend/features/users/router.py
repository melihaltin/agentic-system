from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """Get users (placeholder)."""
    return {"users": [], "message": "Users API - not implemented yet"}

@router.get("/me")
async def get_current_user():
    """Get current user (placeholder)."""
    return {"message": "Current user - not implemented yet"}