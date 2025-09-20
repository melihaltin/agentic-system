from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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


# New Models for Agent Management


class AgentTypeEnum(str, Enum):
    voice = "voice"
    chat = "chat"
    hybrid = "hybrid"


class AvailabilityStatusEnum(str, Enum):
    available = "available"
    coming_soon = "coming_soon"
    beta = "beta"


class SectorResponse(BaseModel):
    """Sector response model"""

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class IntegrationProviderResponse(BaseModel):
    """Integration provider response model"""

    id: str
    name: str
    slug: str
    category: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    documentation_url: Optional[str] = None
    required_credentials: Dict[str, Any]
    oauth_enabled: bool = False
    applicable_sectors: List[str] = []
    is_active: bool = True
    is_beta: bool = False
    created_at: datetime
    updated_at: datetime


class AgentTemplateResponse(BaseModel):
    """Agent template response model"""

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    sector_id: str
    sector: Optional[SectorResponse] = None
    agent_type: AgentTypeEnum
    capabilities: List[str] = []
    default_prompt: Optional[str] = None
    default_voice_id: Optional[str] = None
    requires_voice: bool = False
    pricing_model: Optional[str] = None
    base_price: Optional[float] = None
    icon: Optional[str] = None
    preview_image: Optional[str] = None
    tags: List[str] = []
    configuration_schema: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_featured: bool = False
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime
    required_integrations: List[IntegrationProviderResponse] = []


class CompanyAgentResponse(BaseModel):
    """Company agent response model"""

    id: str
    company_id: str
    agent_template_id: str
    agent_template: Optional[AgentTemplateResponse] = None
    custom_name: Optional[str] = None
    custom_prompt: Optional[str] = None
    selected_voice_id: Optional[str] = None
    selected_voice: Optional[AgentVoiceResponse] = None
    configuration: Dict[str, Any] = {}
    is_active: bool = True
    is_configured: bool = False
    total_interactions: int = 0
    total_minutes_used: float = 0
    last_used_at: Optional[datetime] = None
    monthly_limit: Optional[int] = None
    daily_limit: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime] = None


class CompanyAgentCreate(BaseModel):
    """Create company agent request model"""

    agent_template_id: str
    custom_name: Optional[str] = None
    custom_prompt: Optional[str] = None
    selected_voice_id: Optional[str] = None
    configuration: Dict[str, Any] = {}
    monthly_limit: Optional[int] = None
    daily_limit: Optional[int] = None


class CompanyAgentUpdate(BaseModel):
    """Update company agent request model"""

    custom_name: Optional[str] = None
    custom_prompt: Optional[str] = None
    selected_voice_id: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    monthly_limit: Optional[int] = None
    daily_limit: Optional[int] = None


class ActivateAgentRequest(BaseModel):
    """Request to activate/deactivate an agent"""

    is_active: bool


class AgentTemplatesListResponse(BaseModel):
    """Response for agent templates list"""

    templates: List[AgentTemplateResponse]
    total: int


class CompanyAgentsListResponse(BaseModel):
    """Response for company agents list"""

    agents: List[CompanyAgentResponse]
    total: int
    active_count: int


class SectorsListResponse(BaseModel):
    """Response for sectors list"""

    sectors: List[SectorResponse]
    total: int
