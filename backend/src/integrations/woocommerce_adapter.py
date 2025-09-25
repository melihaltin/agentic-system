"""
WooCommerce Integration Adapter
Implements the BaseIntegrationAdapter for WooCommerce platform
"""

import httpx
import time
import base64
from typing import Dict, Any, List
from src.core.integration_interface import (
    BaseIntegrationAdapter,
    IntegrationConfig,
    APIResponse,
    IntegrationCredentials,
)


class WooCommerceAdapter(BaseIntegrationAdapter):
    """
    WooCommerce platform integration adapter
    """

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = self._build_base_url()
        self.headers = self._build_headers()

    def _build_base_url(self) -> str:
        """Build WooCommerce API base URL"""
        store_url = self.credentials.store_url
        if store_url:
            # Remove trailing slash if present
            store_url = store_url.rstrip("/")
            return f"{store_url}/wp-json/wc/v3"
        return ""

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers for WooCommerce API"""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # WooCommerce uses Basic Auth with consumer key and secret
        if self.credentials.api_key and self.credentials.api_secret:
            credentials = f"{self.credentials.api_key}:{self.credentials.api_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_credentials}"

        return headers

    async def test_connection(self) -> APIResponse:
        """Test connection to WooCommerce API"""
        start_time = time.time()

        try:
            if not self.validate_credentials():
                return APIResponse(
                    success=False,
                    error_message="Missing required credentials for WooCommerce",
                    response_time=time.time() - start_time,
                )

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/system_status", headers=self.headers, timeout=10.0
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    system_data = response.json()
                    return APIResponse(
                        success=True,
                        data={
                            "store_name": system_data.get("settings", {}).get(
                                "title", "Unknown"
                            ),
                            "woocommerce_version": system_data.get("settings", {}).get(
                                "wc_version"
                            ),
                            "wordpress_version": system_data.get("settings", {}).get(
                                "wp_version"
                            ),
                            "currency": system_data.get("settings", {}).get("currency"),
                            "timezone": system_data.get("settings", {}).get("timezone"),
                        },
                        status_code=response.status_code,
                        response_time=response_time,
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=f"WooCommerce API error: {response.status_code} - {response.text}",
                        status_code=response.status_code,
                        response_time=response_time,
                    )

        except httpx.TimeoutException:
            return APIResponse(
                success=False,
                error_message="Connection timeout to WooCommerce API",
                response_time=time.time() - start_time,
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error_message=f"Unexpected error connecting to WooCommerce: {str(e)}",
                response_time=time.time() - start_time,
            )

    async def get_products(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """Fetch products from WooCommerce"""
        start_time = time.time()

        try:
            params = {
                "per_page": min(limit, 100),  # WooCommerce max limit is 100
                "page": (offset // limit) + 1,
                "status": "publish",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    products_data = response.json()
                    return APIResponse(
                        success=True,
                        data={
                            "products": products_data,
                            "total_count": len(products_data),
                            "limit": limit,
                            "offset": offset,
                            "page": params["page"],
                        },
                        status_code=response.status_code,
                        response_time=response_time,
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=f"Failed to fetch products: {response.status_code} - {response.text}",
                        status_code=response.status_code,
                        response_time=response_time,
                    )

        except Exception as e:
            return APIResponse(
                success=False,
                error_message=f"Error fetching products: {str(e)}",
                response_time=time.time() - start_time,
            )

    async def get_orders(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """Fetch orders from WooCommerce"""
        start_time = time.time()

        try:
            params = {
                "per_page": min(limit, 100),
                "page": (offset // limit) + 1,
                "status": "any",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orders",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    orders_data = response.json()
                    return APIResponse(
                        success=True,
                        data={
                            "orders": orders_data,
                            "total_count": len(orders_data),
                            "limit": limit,
                            "offset": offset,
                            "page": params["page"],
                        },
                        status_code=response.status_code,
                        response_time=response_time,
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=f"Failed to fetch orders: {response.status_code} - {response.text}",
                        status_code=response.status_code,
                        response_time=response_time,
                    )

        except Exception as e:
            return APIResponse(
                success=False,
                error_message=f"Error fetching orders: {str(e)}",
                response_time=time.time() - start_time,
            )

    async def get_customers(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """Fetch customers from WooCommerce"""
        start_time = time.time()

        try:
            params = {
                "per_page": min(limit, 100),
                "page": (offset // limit) + 1,
                "role": "customer",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    customers_data = response.json()
                    return APIResponse(
                        success=True,
                        data={
                            "customers": customers_data,
                            "total_count": len(customers_data),
                            "limit": limit,
                            "offset": offset,
                            "page": params["page"],
                        },
                        status_code=response.status_code,
                        response_time=response_time,
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=f"Failed to fetch customers: {response.status_code} - {response.text}",
                        status_code=response.status_code,
                        response_time=response_time,
                    )

        except Exception as e:
            return APIResponse(
                success=False,
                error_message=f"Error fetching customers: {str(e)}",
                response_time=time.time() - start_time,
            )

    async def search_products(self, query: str, limit: int = 20) -> APIResponse:
        """Search for products on WooCommerce"""
        start_time = time.time()

        try:
            params = {"per_page": min(limit, 100), "search": query, "status": "publish"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    products_data = response.json()
                    return APIResponse(
                        success=True,
                        data={
                            "products": products_data,
                            "search_query": query,
                            "total_results": len(products_data),
                            "limit": limit,
                        },
                        status_code=response.status_code,
                        response_time=response_time,
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=f"Failed to search products: {response.status_code} - {response.text}",
                        status_code=response.status_code,
                        response_time=response_time,
                    )

        except Exception as e:
            return APIResponse(
                success=False,
                error_message=f"Error searching products: {str(e)}",
                response_time=time.time() - start_time,
            )

    def get_supported_webhook_events(self) -> List[str]:
        """Get supported WooCommerce webhook events"""
        return [
            "order.created",
            "order.updated",
            "order.deleted",
            "product.created",
            "product.updated",
            "product.deleted",
            "customer.created",
            "customer.updated",
            "customer.deleted",
            "coupon.created",
            "coupon.updated",
            "coupon.deleted",
        ]

    def validate_credentials(self) -> bool:
        """Validate WooCommerce credentials"""
        return bool(
            self.credentials.store_url
            and self.credentials.api_key
            and self.credentials.api_secret
        )
