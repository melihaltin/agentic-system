"""
Polling API Router
FastAPI router for polling service endpoints
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any, List
from src.services.agent_integration_service_v2 import AgentIntegrationService
from src.services.polling_service import AgentIntegrationPoller

router = APIRouter(prefix="/polling", tags=["polling"])

# Global poller instance
_poller_instance = None


@router.get("/agents/integrations")
async def get_agents_with_integrations() -> Dict[str, Any]:
    """
    Get all active agents with their integration configurations
    """
    try:
        service = AgentIntegrationService()
        agents_data = await service.fetch_agents_with_integrations()

        return {
            "success": True,
            "data": agents_data,
            "total_agents": len(agents_data),
            "message": f"Successfully fetched {len(agents_data)} agents with integrations",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agents with integrations: {str(e)}",
        )


@router.get("/company/{company_id}/integrations")
async def get_company_integration_status(company_id: str) -> Dict[str, Any]:
    """
    Get integration status for a specific company
    """
    try:
        service = AgentIntegrationService()
        company_data = await service.fetch_company_integration_status(company_id)

        return {
            "success": True,
            "data": company_data,
            "message": f"Successfully fetched integration status for company {company_id}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch company integration status: {str(e)}",
        )


@router.post("/start")
async def start_polling(
    background_tasks: BackgroundTasks, interval: int = 30
) -> Dict[str, Any]:
    """
    Start the polling service

    Args:
        interval: Polling interval in seconds (default: 30)
    """
    global _poller_instance

    try:
        if _poller_instance and _poller_instance.is_running:
            return {
                "success": False,
                "message": "Polling service is already running",
                "status": _poller_instance.get_status(),
            }

        _poller_instance = AgentIntegrationPoller(polling_interval=interval)

        # Start polling in background
        background_tasks.add_task(_poller_instance.start_polling)

        return {
            "success": True,
            "message": f"Polling service started with {interval}s interval",
            "status": _poller_instance.get_status(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start polling service: {str(e)}"
        )


@router.post("/stop")
async def stop_polling() -> Dict[str, Any]:
    """
    Stop the polling service
    """
    global _poller_instance

    try:
        if not _poller_instance or not _poller_instance.is_running:
            return {"success": False, "message": "Polling service is not running"}

        await _poller_instance.stop_polling()

        return {
            "success": True,
            "message": "Polling service stopped",
            "status": _poller_instance.get_status(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to stop polling service: {str(e)}"
        )


@router.get("/status")
async def get_polling_status() -> Dict[str, Any]:
    """
    Get current polling service status
    """
    global _poller_instance

    if not _poller_instance:
        return {
            "success": True,
            "status": {
                "is_running": False,
                "polling_interval": None,
                "poll_count": 0,
                "last_poll_time": None,
            },
            "message": "Polling service not initialized",
        }

    return {
        "success": True,
        "status": _poller_instance.get_status(),
        "message": "Polling service status retrieved",
    }


@router.post("/poll-once")
async def poll_once() -> Dict[str, Any]:
    """
    Perform a single poll operation
    """
    try:
        service = AgentIntegrationService()
        agents_data = await service.fetch_agents_with_integrations()

        return {
            "success": True,
            "data": agents_data,
            "total_agents": len(agents_data),
            "message": f"Single poll completed - found {len(agents_data)} agents with integrations",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to perform single poll: {str(e)}"
        )


@router.post("/start-abandoned-cart")
async def start_abandoned_cart_polling(
    background_tasks: BackgroundTasks, interval: int = 30
) -> Dict[str, Any]:
    """
    Start the abandoned cart polling service
    
    Args:
        interval: Polling interval in seconds (default: 30)
    """
    global _poller_instance

    try:
        if _poller_instance and _poller_instance.is_running:
            return {
                "success": False,
                "message": "Abandoned cart polling service is already running",
                "status": _poller_instance.get_status(),
            }

        _poller_instance = AgentIntegrationPoller(polling_interval=interval)

        # Start polling in background
        background_tasks.add_task(_poller_instance.start_polling)

        return {
            "success": True,
            "message": f"Abandoned cart polling service started with {interval}s interval",
            "status": _poller_instance.get_status(),
            "description": "System will automatically detect abandoned cart agents, generate mock data, and send to external APIs",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start abandoned cart polling: {str(e)}"
        )


@router.post("/abandoned-cart/test-once")
async def test_abandoned_cart_once() -> Dict[str, Any]:
    """
    Test abandoned cart processing once
    """
    try:
        poller = AgentIntegrationPoller(polling_interval=30)
        await poller.poll_once()

        return {
            "success": True,
            "message": "Abandoned cart test completed successfully",
            "description": "Check logs for detailed processing information",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to test abandoned cart processing: {str(e)}"
        )
