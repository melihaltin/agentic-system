"""
Abandoned Cart API Router
FastAPI router for abandoned cart recovery operations
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from src.services.abandoned_cart_service import AbandonedCartAgentService
from pydantic import BaseModel

router = APIRouter(prefix="/abandoned-cart", tags=["abandoned-cart"])

# Global service instance
_abandoned_cart_service = None


class ExternalAPIRequest(BaseModel):
    """Model for external API request"""
    api_url: str
    api_key: Optional[str] = None


def get_abandoned_cart_service() -> AbandonedCartAgentService:
    """Get or create abandoned cart service instance"""
    global _abandoned_cart_service
    if _abandoned_cart_service is None:
        _abandoned_cart_service = AbandonedCartAgentService()
    return _abandoned_cart_service


@router.get("/agents")
async def get_abandoned_cart_agents() -> Dict[str, Any]:
    """
    Get all agents configured for abandoned cart recovery
    """
    try:
        service = get_abandoned_cart_service()
        agents = await service.get_abandoned_cart_agents()
        
        return {
            "success": True,
            "message": f"Found {len(agents)} abandoned cart agents",
            "agents": agents,
            "total_agents": len(agents)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get abandoned cart agents: {str(e)}"
        )


@router.post("/initialize")
async def initialize_abandoned_cart_integrations() -> Dict[str, Any]:
    """
    Initialize integrations for all abandoned cart agents
    """
    try:
        service = get_abandoned_cart_service()
        result = await service.initialize_abandoned_cart_integrations()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize abandoned cart integrations: {str(e)}"
        )


@router.get("/data/{agent_id}/{provider_slug}")
async def fetch_abandoned_cart_data(agent_id: str, provider_slug: str) -> Dict[str, Any]:
    """
    Fetch abandoned cart data for a specific agent and platform
    
    Args:
        agent_id: Agent identifier
        provider_slug: Platform identifier (shopify, woocommerce, etc.)
    """
    try:
        service = get_abandoned_cart_service()
        result = await service.fetch_abandoned_cart_data(agent_id, provider_slug)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch abandoned cart data: {str(e)}"
        )


@router.get("/payload/{agent_id}")
async def create_abandoned_cart_payload(agent_id: str) -> Dict[str, Any]:
    """
    Create complete payload for abandoned cart recovery for a specific agent
    
    Args:
        agent_id: Agent identifier
    """
    try:
        service = get_abandoned_cart_service()
        result = await service.create_abandoned_cart_payload(agent_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create abandoned cart payload: {str(e)}"
        )


@router.post("/send/{agent_id}")
async def send_abandoned_cart_payload(
    agent_id: str,
    api_request: ExternalAPIRequest = Body(...)
) -> Dict[str, Any]:
    """
    Create and send abandoned cart payload to external API
    
    Args:
        agent_id: Agent identifier
        api_request: External API configuration
    """
    try:
        service = get_abandoned_cart_service()
        
        # Create payload
        payload_result = await service.create_abandoned_cart_payload(agent_id)
        
        if not payload_result["success"]:
            return payload_result
        
        # Send to external API
        send_result = await service.send_to_external_api(
            payload=payload_result["payload"],
            api_url=api_request.api_url,
            api_key=api_request.api_key
        )
        
        return {
            "success": send_result["success"],
            "message": send_result["message"],
            "agent_id": agent_id,
            "payload_created": True,
            "api_response": {
                "status_code": send_result["status_code"],
                "response_data": send_result["response_data"],
                "api_url": send_result["api_url"]
            },
            "payload_summary": payload_result["payload"]["summary"] if payload_result["payload"] else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send abandoned cart payload: {str(e)}"
        )


@router.get("/mock-data/{provider_slug}")
async def generate_mock_abandoned_cart_data(
    provider_slug: str,
    company_name: str = Query("Sample Company", description="Company name for mock data")
) -> Dict[str, Any]:
    """
    Generate mock abandoned cart data for testing
    
    Args:
        provider_slug: Platform identifier
        company_name: Company name to use in mock data
    """
    try:
        service = get_abandoned_cart_service()
        
        mock_company_info = {
            "company_name": company_name,
            "website": f"{company_name.lower().replace(' ', '')}.com"
        }
        
        mock_data = service.generate_mock_abandoned_cart_data(provider_slug, mock_company_info)
        
        return {
            "success": True,
            "message": f"Generated mock abandoned cart data for {provider_slug}",
            "data": mock_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate mock data: {str(e)}"
        )


# Convenience endpoints for batch operations


@router.post("/process-all")
async def process_all_abandoned_cart_agents() -> Dict[str, Any]:
    """
    Process all abandoned cart agents and create payloads
    """
    try:
        service = get_abandoned_cart_service()
        
        # Get all abandoned cart agents
        agents = await service.get_abandoned_cart_agents()
        
        if not agents:
            return {
                "success": True,
                "message": "No abandoned cart agents found",
                "results": [],
                "total_processed": 0
            }
        
        # Process each agent
        results = []
        for agent in agents:
            agent_id = agent["agent_id"]
            
            try:
                payload_result = await service.create_abandoned_cart_payload(agent_id)
                results.append({
                    "agent_id": agent_id,
                    "agent_name": agent["agent_info"].get("custom_name", "Unnamed"),
                    "company_name": agent.get("company_info", {}).get("company_name", "Unknown"),
                    "success": payload_result["success"],
                    "message": payload_result["message"],
                    "payload_summary": payload_result["payload"]["summary"] if payload_result.get("payload") else None
                })
            except Exception as e:
                results.append({
                    "agent_id": agent_id,
                    "agent_name": agent["agent_info"].get("custom_name", "Unnamed"),
                    "company_name": agent.get("company_info", {}).get("company_name", "Unknown"),
                    "success": False,
                    "message": f"Error processing agent: {str(e)}",
                    "payload_summary": None
                })
        
        successful_results = [r for r in results if r["success"]]
        
        return {
            "success": True,
            "message": f"Processed {len(agents)} abandoned cart agents",
            "results": results,
            "total_processed": len(agents),
            "successful": len(successful_results),
            "failed": len(agents) - len(successful_results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process abandoned cart agents: {str(e)}"
        )
