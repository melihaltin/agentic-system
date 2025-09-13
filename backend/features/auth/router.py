from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def auth_root():
    """Auth root endpoint - redirects to Supabase auth."""
    return {
        "message": "Authentication API", 
        "note": "Use /auth/supabase endpoints for business authentication"
    }