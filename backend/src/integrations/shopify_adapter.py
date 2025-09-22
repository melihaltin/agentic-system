"""
Shopify Integration Adapter
Implements the BaseIntegrationAdapter for Shopify platform
"""

import httpx
import time
from typing import Dict, Any, List
from src.core.integration_interface import (
    BaseIntegrationAdapter,
    IntegrationConfig,
    APIResponse,
    IntegrationCredentials,
)


class ShopifyAdapter(BaseIntegrationAdapter):
    """
    Shopify platform integration adapter
    """

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = self._build_base_url()
        self.headers = self._build_headers()

    def _build_base_url(self) -> str:
        """Build Shopify API base URL"""
        store_url = self.credentials.store_url
        if store_url:
            # Remove protocol and trailing slash if present
            store_url = (
                store_url.replace("https://", "").replace("http://", "").rstrip("/")
            )
            return f"https://{store_url}.myshopify.com/admin/api/2023-10"
        return ""

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers for Shopify API"""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self.credentials.access_token:
            headers["X-Shopify-Access-Token"] = self.credentials.access_token
        elif self.credentials.api_key and self.credentials.api_secret:
            # For private apps using API key and password
            headers["Authorization"] = (
                f"Basic {self.credentials.api_key}:{self.credentials.api_secret}"
            )

        return headers

    async def test_connection(self) -> APIResponse:
        """Test connection to Shopify API"""
        start_time = time.time()

        try:
            if not self.validate_credentials():
                return APIResponse(
                    success=False,
                    error_message="Missing required credentials for Shopify",
                    response_time=time.time() - start_time,
                )

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/shop.json", headers=self.headers, timeout=10.0
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    shop_data = response.json().get("shop", {})
                    return APIResponse(
                        success=True,
                        data={
                            "shop_name": shop_data.get("name"),
                            "shop_domain": shop_data.get("domain"),
                            "shop_email": shop_data.get("email"),
                            "currency": shop_data.get("currency"),
                            "timezone": shop_data.get("timezone"),
                        },
                        status_code=response.status_code,
                        response_time=response_time,
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=f"Shopify API error: {response.status_code} - {response.text}",
                        status_code=response.status_code,
                        response_time=response_time,
                    )

        except httpx.TimeoutException:
            return APIResponse(
                success=False,
                error_message="Connection timeout to Shopify API",
                response_time=time.time() - start_time,
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error_message=f"Unexpected error connecting to Shopify: {str(e)}",
                response_time=time.time() - start_time,
            )

    async def get_products(self, limit: int = 50, offset: int = 0) -> APIResponse:
        """Fetch products from Shopify"""
        start_time = time.time()

        try:
            params = {
                "limit": min(limit, 250),  # Shopify max limit is 250
                "offset": offset,
                "fields": "id,title,handle,vendor,product_type,created_at,updated_at,status,variants",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products.json",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    products_data = response.json().get("products", [])
                    return APIResponse(
                        success=True,
                        data={
                            "products": products_data,
                            "total_count": len(products_data),
                            "limit": limit,
                            "offset": offset,
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
        """Fetch orders from Shopify"""
        start_time = time.time()

        try:
            params = {
                "limit": min(limit, 250),
                "offset": offset,
                "status": "any",
                "fields": "id,order_number,email,created_at,updated_at,total_price,currency,customer",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/orders.json",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    orders_data = response.json().get("orders", [])
                    return APIResponse(
                        success=True,
                        data={
                            "orders": orders_data,
                            "total_count": len(orders_data),
                            "limit": limit,
                            "offset": offset,
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
        """Fetch customers from Shopify"""
        start_time = time.time()

        try:
            params = {
                "limit": min(limit, 250),
                "offset": offset,
                "fields": "id,email,first_name,last_name,phone,created_at,updated_at,orders_count,total_spent",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/customers.json",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    customers_data = response.json().get("customers", [])
                    return APIResponse(
                        success=True,
                        data={
                            "customers": customers_data,
                            "total_count": len(customers_data),
                            "limit": limit,
                            "offset": offset,
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
        """Search for products on Shopify"""
        start_time = time.time()

        try:
            params = {
                "limit": min(limit, 250),
                "title": query,  # Search by title
                "fields": "id,title,handle,vendor,product_type,variants",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/products.json",
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    products_data = response.json().get("products", [])
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
        """Get supported Shopify webhook events"""
        return [
            "orders/create",
            "orders/updated",
            "orders/paid",
            "orders/cancelled",
            "orders/fulfilled",
            "orders/partially_fulfilled",
            "products/create",
            "products/update",
            "products/delete",
            "customers/create",
            "customers/update",
            "customers/delete",
            "carts/create",
            "carts/update",
            "checkouts/create",
            "checkouts/update",
            "checkouts/delete",
        ]

    def validate_credentials(self) -> bool:
        """Validate Shopify credentials"""
        # Check if we have either access token or API key + secret
        has_access_token = bool(self.credentials.access_token)
        has_api_key_secret = bool(
            self.credentials.api_key and self.credentials.api_secret
        )
        has_store_url = bool(self.credentials.store_url)

        return has_store_url and (has_access_token or has_api_key_secret)
