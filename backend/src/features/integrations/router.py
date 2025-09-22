"""
Integration API Router
FastAPI router for platform integration endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from src.services.integration_service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])

# Global integration service instance
_integration_service = None


def get_integration_service() -> IntegrationService:
    """Get or create integration service instance"""
    global _integration_service
    if _integration_service is None:
        _integration_service = IntegrationService()
    return _integration_service


@router.post("/initialize")
async def initialize_integrations() -> Dict[str, Any]:
    """
    Initialize all platform integrations
    """
    try:
        service = get_integration_service()
        result = await service.initialize_integrations()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize integrations: {str(e)}"
        )


@router.get("/providers")
async def get_available_providers() -> Dict[str, Any]:
    """
    Get list of available integration providers
    """
    try:
        service = get_integration_service()
        providers = service.get_available_providers()
        return {
            "success": True,
            "providers": providers,
            "total_providers": len(providers),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get providers: {str(e)}"
        )


@router.get("/status")
async def get_integrations_status() -> Dict[str, Any]:
    """
    Get summary of all active integrations
    """
    try:
        service = get_integration_service()
        summary = service.get_active_integrations_summary()
        return {"success": True, "summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get integrations status: {str(e)}"
        )


@router.post("/test/{agent_id}/{provider_slug}")
async def test_integration_connection(
    agent_id: str, provider_slug: str
) -> Dict[str, Any]:
    """
    Test connection for a specific integration

    Args:
        agent_id: Agent identifier
        provider_slug: Platform identifier (shopify, woocommerce, etc.)
    """
    try:
        service = get_integration_service()
        result = await service.test_integration_connection(agent_id, provider_slug)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to test connection: {str(e)}"
        )


@router.get("/status/{agent_id}/{provider_slug}")
async def get_integration_status(agent_id: str, provider_slug: str) -> Dict[str, Any]:
    """
    Get detailed status for a specific integration

    Args:
        agent_id: Agent identifier
        provider_slug: Platform identifier
    """
    try:
        service = get_integration_service()
        result = await service.get_integration_status(agent_id, provider_slug)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get integration status: {str(e)}"
        )


@router.get("/data/{agent_id}/{provider_slug}/{data_type}")
async def fetch_platform_data(
    agent_id: str,
    provider_slug: str,
    data_type: str,
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    query: Optional[str] = Query(None, description="Search query for products"),
) -> Dict[str, Any]:
    """
    Fetch data from a platform integration

    Args:
        agent_id: Agent identifier
        provider_slug: Platform identifier (shopify, woocommerce, etc.)
        data_type: Type of data (products, orders, customers)
        limit: Maximum number of items to fetch
        offset: Number of items to skip
        query: Search query (for product search)
    """
    try:
        # Validate data type
        valid_data_types = ["products", "orders", "customers"]
        if data_type not in valid_data_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data type. Must be one of: {', '.join(valid_data_types)}",
            )

        service = get_integration_service()
        result = await service.fetch_platform_data(
            agent_id=agent_id,
            provider_slug=provider_slug,
            data_type=data_type,
            limit=limit,
            offset=offset,
            query=query,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch platform data: {str(e)}"
        )


@router.post("/reload")
async def reload_integrations() -> Dict[str, Any]:
    """
    Reload all integrations (clear cache and reinitialize)
    """
    try:
        service = get_integration_service()
        result = await service.reload_integrations()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reload integrations: {str(e)}"
        )


# Convenience endpoints for specific operations


@router.get("/products/{agent_id}/{provider_slug}")
async def get_products(
    agent_id: str,
    provider_slug: str,
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """
    Get products from a platform integration
    """
    return await fetch_platform_data(agent_id, provider_slug, "products", limit, offset)


@router.get("/orders/{agent_id}/{provider_slug}")
async def get_orders(
    agent_id: str,
    provider_slug: str,
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """
    Get orders from a platform integration
    """
    return await fetch_platform_data(agent_id, provider_slug, "orders", limit, offset)


@router.get("/customers/{agent_id}/{provider_slug}")
async def get_customers(
    agent_id: str,
    provider_slug: str,
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """
    Get customers from a platform integration
    """
    return await fetch_platform_data(
        agent_id, provider_slug, "customers", limit, offset
    )


@router.get("/search/products/{agent_id}/{provider_slug}")
async def search_products(
    agent_id: str,
    provider_slug: str,
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    Search products on a platform integration
    """
    return await fetch_platform_data(
        agent_id, provider_slug, "products", limit, 0, query
    )
