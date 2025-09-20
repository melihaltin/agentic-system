from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from src.features.agents.service import elevenlabs_service
from src.features.agents.models import AgentVoicesListResponse, SyncVoicesResponse

router = APIRouter(prefix="/v1/voices", tags=["voices"])


@router.post("/sync", response_model=SyncVoicesResponse)
async def sync_voices_from_elevenlabs():
    """
    Sync voices from ElevenLabs API to database.
    This endpoint fetches all voices from ElevenLabs and saves them to the agent_voices table.
    """
    try:
        result = await elevenlabs_service.sync_voices_from_elevenlabs()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync voices: {str(e)}")


@router.get("/", response_model=AgentVoicesListResponse)
async def get_voices(is_active: Optional[bool] = True):
    """
    Get all voices from database.

    Args:
        is_active: Filter by active status. Default is True. Set to None to get all voices.

    Returns:
        List of agent voices with total count
    """
    try:
        voices = await elevenlabs_service.get_voices_from_database(is_active=is_active)

        return AgentVoicesListResponse(voices=voices, total=len(voices))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch voices: {str(e)}")


@router.get("/providers/elevenlabs")
async def get_elevenlabs_voices():
    """
    Get voices directly from ElevenLabs API (for testing purposes).
    This endpoint bypasses the database and fetches voices directly from ElevenLabs.
    """
    try:
        voices = await elevenlabs_service.fetch_voices_from_elevenlabs()
        return {"voices": [voice.dict() for voice in voices], "total": len(voices)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch voices from ElevenLabs: {str(e)}"
        )
