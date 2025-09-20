from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ElevenLabsVoice(BaseModel):
    """Model for ElevenLabs API voice response"""

    voice_id: str
    name: str
    category: Optional[str] = None
    labels: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    preview_url: Optional[str] = None
    available_for_tiers: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class AgentVoiceResponse(BaseModel):
    """Response model for agent voice"""

    id: str
    name: str
    provider: str
    voice_id: str
    language: str
    gender: Optional[str] = None
    age_group: Optional[str] = None
    accent: Optional[str] = None
    sample_url: Optional[str] = None
    is_premium: bool = False
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class AgentVoicesListResponse(BaseModel):
    """Response model for list of agent voices"""

    voices: List[AgentVoiceResponse]
    total: int


class SyncVoicesResponse(BaseModel):
    """Response model for sync operation"""

    success: bool
    message: str
    synced_count: int
    skipped_count: int
    errors: List[str] = []
