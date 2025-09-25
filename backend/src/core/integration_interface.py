"""
Base Integration Interface
Defines the common interface for all platform integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class IntegrationStatus(Enum):
    """Integration status enumeration"""

    ACTIVE = "active"
    PENDING = "pending"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class IntegrationCredentials:
    """Standardized credentials structure"""

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    store_url: Optional[str] = None
    access_token: Optional[str] = None
    webhook_secret: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = None


@dataclass
class IntegrationConfig:
    """Integration configuration structure"""

    provider_slug: str
    provider_name: str
    agent_id: str
    company_id: str
    credentials: IntegrationCredentials
    webhook_url: Optional[str] = None
    is_enabled: bool = True
    settings: Optional[Dict[str, Any]] = None


@dataclass
class APIResponse:
    """Standardized API response structure"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None


class BaseIntegrationAdapter(ABC):
    """
    Abstract base class for all platform integration adapters
    """

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.provider_slug = config.provider_slug
        self.provider_name = config.provider_name
        self.credentials = config.credentials
        self.is_enabled = config.is_enabled

    @abstractmethod
    async def test_connection(self) -> APIResponse:
        """
        Test the connection to the platform API

        Returns:
            APIResponse with connection test results
        """
        pass

    @abstractmethod
    async def get_products(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """
        Fetch products from the platform

        Args:
            limit: Maximum number of products to fetch
            offset: Number of products to skip

        Returns:
            APIResponse containing products data
        """
        pass

    @abstractmethod
    async def get_orders(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """
        Fetch orders from the platform

        Args:
            limit: Maximum number of orders to fetch
            offset: Number of orders to skip

        Returns:
            APIResponse containing orders data
        """
        pass

    @abstractmethod
    async def get_customers(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """
        Fetch customers from the platform

        Args:
            limit: Maximum number of customers to fetch
            offset: Number of customers to skip

        Returns:
            APIResponse containing customers data
        """
        pass

    @abstractmethod
    async def search_products(self, query: str, limit: int = 20) -> APIResponse:
        """
        Search for products on the platform

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            APIResponse containing search results
        """
        pass

    async def get_integration_status(self) -> Dict[str, Any]:
        """
        Get current integration status

        Returns:
            Dict containing status information
        """
        connection_test = await self.test_connection()

        return {
            "provider_slug": self.provider_slug,
            "provider_name": self.provider_name,
            "agent_id": self.config.agent_id,
            "is_enabled": self.is_enabled,
            "connection_status": (
                IntegrationStatus.ACTIVE.value
                if connection_test.success
                else IntegrationStatus.ERROR.value
            ),
            "last_test": connection_test.response_time,
            "error_message": (
                connection_test.error_message if not connection_test.success else None
            ),
        }

    def get_webhook_config(self) -> Optional[Dict[str, Any]]:
        """
        Get webhook configuration for the platform

        Returns:
            Dict containing webhook configuration or None
        """
        if self.config.webhook_url:
            return {
                "webhook_url": self.config.webhook_url,
                "webhook_secret": self.credentials.webhook_secret,
                "events": self.get_supported_webhook_events(),
            }
        return None

    @abstractmethod
    def get_supported_webhook_events(self) -> List[str]:
        """
        Get list of supported webhook events for this platform

        Returns:
            List of supported webhook event names
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validate if all required credentials are provided

        Returns:
            True if credentials are valid, False otherwise
        """
        pass
