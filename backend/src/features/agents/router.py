from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging
from src.features.agents.service import elevenlabs_service, agent_service
from src.features.agents.models import (
    AgentVoicesListResponse,
    SyncVoicesResponse,
    SectorsListResponse,
    AgentTemplatesListResponse,
    CompanyAgentsListResponse,
    CompanyAgentCreate,
    CompanyAgentUpdate,
    ActivateAgentRequest,
    SectorResponse,
    AgentTemplateResponse,
    CompanyAgentResponse,
)
from src.features.shared.dependencies import get_current_user

logger = logging.getLogger(__name__)

# Voice routes
voice_router = APIRouter(prefix="/v1/voices", tags=["voices"])

# Agent management routes
agent_router = APIRouter(prefix="/v1/agents", tags=["agents"])


# Voice Routes
@voice_router.post("/sync", response_model=SyncVoicesResponse)
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


@voice_router.get("/", response_model=AgentVoicesListResponse)
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


@voice_router.get("/providers/elevenlabs")
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


# Agent Management Routes
@agent_router.get("/sectors")
async def get_sectors():
    """Get all active sectors"""
    try:
        sectors = await agent_service.get_sectors()
        return {"sectors": sectors, "total": len(sectors)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch sectors: {str(e)}"
        )


@agent_router.get("/sectors/{sector_id}/templates")
async def get_agent_templates_by_sector(sector_id: str):
    """Get available agent templates for a sector"""
    try:
        templates = await agent_service.get_agent_templates_by_sector(sector_id)
        return {"templates": templates, "total": len(templates)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch templates: {str(e)}"
        )


@agent_router.get("/company/{company_id}")
async def get_company_agents(company_id: str):
    """Get all agents for a company"""
    try:
        agents = await agent_service.get_company_agents(company_id)
        active_count = sum(1 for agent in agents if agent.get("is_active"))
        return {"agents": agents, "total": len(agents), "active_count": active_count}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch company agents: {str(e)}"
        )


@agent_router.post("/company/{company_id}/activate/{agent_template_id}")
async def activate_agent(
    company_id: str, agent_template_id: str, config: Optional[dict] = None
):
    """Activate an agent template for a company with configuration"""
    try:
        agent = await agent_service.activate_agent_for_company(
            company_id, agent_template_id, config or {}
        )
        return {"success": True, "agent": agent}
    except Exception as e:
        logger.error(f"Failed to activate agent: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to activate agent: {str(e)}"
        )


@agent_router.put("/company/{company_id}/agents/{agent_id}")
async def update_company_agent(company_id: str, agent_id: str, updates: dict):
    """Update company agent configuration and integrations"""
    try:
        agent = await agent_service.update_company_agent(company_id, agent_id, updates)
        return {"success": True, "agent": agent}
    except Exception as e:
        logger.error(f"Failed to update agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")


@agent_router.put("/company/{company_id}/agents/{agent_id}/toggle")
async def toggle_agent_status(
    company_id: str, agent_id: str, request: ActivateAgentRequest
):
    """Toggle agent active/inactive status"""
    try:
        agent = await agent_service.toggle_agent_status(
            company_id, agent_id, request.is_active
        )

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {"success": True, "agent": agent}
    except Exception as e:
        logger.error(f"Error toggling agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle agent: {str(e)}")


@agent_router.get("/company/{company_id}/agents/{agent_id}/integrations")
async def get_agent_integrations(company_id: str, agent_id: str):
    """Get integration configurations for an agent"""
    try:
        from src.features.agents.service import IntegrationService

        integrations = await IntegrationService.get_agent_integrations(agent_id)
        return {"success": True, "integrations": integrations}
    except Exception as e:
        logger.error(f"Failed to get agent integrations: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent integrations: {str(e)}"
        )


@agent_router.get("/integrations")
async def get_integration_providers(category: Optional[str] = None):
    """Get integration providers"""
    try:
        providers = await agent_service.get_integration_providers(category)
        return {"providers": providers, "total": len(providers)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch providers: {str(e)}"
        )


# Export routers
router = voice_router  # For backward compatibility
