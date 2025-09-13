"""
Tests for the e-commerce agent functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from agents.ecommerce.agent import EcommerceAgent
from agents.ecommerce.tools import (
    ProductSearchTool,
    CartManagementTool,
    OrderProcessingTool,
)


class TestEcommerceAgent:
    """Test cases for the EcommerceAgent class."""

    @pytest.fixture
    def agent(self):
        """Create an EcommerceAgent instance for testing."""
        return EcommerceAgent()

    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        return {"user_id": "test_user_123", "session_id": "session_456"}

    def test_agent_initialization(self, agent):
        """Test that the agent initializes correctly."""
        assert agent.name == "ecommerce"
        assert "e-commerce operations" in agent.description
        assert len(agent.tools) == 4  # 4 tools should be initialized
        assert "product_search" in agent.tools
        assert "cart_management" in agent.tools
        assert "order_processing" in agent.tools
        assert "product_recommendations" in agent.tools

    def test_get_tools(self, agent):
        """Test that get_tools returns the correct tools."""
        tools = agent.get_tools()
        assert len(tools) == 4
        assert all(hasattr(tool, "execute") for tool in tools)

    def test_get_capabilities(self, agent):
        """Test that get_capabilities returns expected capabilities."""
        capabilities = agent.get_capabilities()
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert "Product search and discovery" in capabilities
        assert "Shopping cart management" in capabilities

    @pytest.mark.asyncio
    async def test_product_search_message(self, agent, sample_context):
        """Test processing a product search message."""
        message = "search for headphones"
        response = await agent.process_message(message, sample_context)

        assert isinstance(response, str)
        assert "found" in response.lower() or "search" in response.lower()
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_cart_message(self, agent, sample_context):
        """Test processing a cart-related message."""
        message = "add to cart"
        response = await agent.process_message(message, sample_context)

        assert isinstance(response, str)
        assert "cart" in response.lower()
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_order_message(self, agent, sample_context):
        """Test processing an order-related message."""
        message = "create order"
        response = await agent.process_message(message, sample_context)

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_recommendation_message(self, agent, sample_context):
        """Test processing a recommendation request."""
        message = "recommend products"
        response = await agent.process_message(message, sample_context)

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_general_message(self, agent, sample_context):
        """Test processing a general inquiry."""
        message = "hello"
        response = await agent.process_message(message, sample_context)

        assert isinstance(response, str)
        assert "e-commerce assistant" in response.lower()
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_message_without_context(self, agent):
        """Test processing a message without context."""
        message = "search for products"
        response = await agent.process_message(message)

        assert isinstance(response, str)
        assert len(response) > 0


class TestProductSearchTool:
    """Test cases for the ProductSearchTool class."""

    @pytest.fixture
    def tool(self):
        """Create a ProductSearchTool instance for testing."""
        return ProductSearchTool()

    @pytest.mark.asyncio
    async def test_search_by_query(self, tool):
        """Test searching products by query."""
        results = await tool.execute("headphones")

        assert isinstance(results, list)
        assert len(results) > 0
        assert all("name" in product for product in results)
        assert all("price" in product for product in results)

    @pytest.mark.asyncio
    async def test_search_with_category_filter(self, tool):
        """Test searching with category filter."""
        results = await tool.execute("", category="Electronics")

        # Since we're searching with empty query, we might get no results
        # but the function should not raise an error
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_price_filter(self, tool):
        """Test searching with price filter."""
        results = await tool.execute("", max_price=50.00)

        assert isinstance(results, list)
        # All results should be under the price limit
        for product in results:
            assert product["price_numeric"] <= 50.00

    @pytest.mark.asyncio
    async def test_search_with_limit(self, tool):
        """Test searching with result limit."""
        results = await tool.execute("", limit=2)

        assert isinstance(results, list)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_search_no_results(self, tool):
        """Test search that returns no results."""
        results = await tool.execute("nonexistentproduct12345")

        assert isinstance(results, list)
        assert len(results) == 0


class TestCartManagementTool:
    """Test cases for the CartManagementTool class."""

    @pytest.fixture
    def tool(self):
        """Create a CartManagementTool instance for testing."""
        return CartManagementTool()

    @pytest.mark.asyncio
    async def test_add_to_cart(self, tool):
        """Test adding item to cart."""
        result = await tool.execute("add", "test_user", product_id=1, quantity=2)

        assert result["success"] is True
        assert "cart" in result
        assert result["total_items"] == 2

    @pytest.mark.asyncio
    async def test_view_empty_cart(self, tool):
        """Test viewing empty cart."""
        result = await tool.execute("view", "new_user")

        assert result["success"] is True
        assert result["total_items"] == 0
        assert len(result["cart"]) == 0

    @pytest.mark.asyncio
    async def test_add_same_item_twice(self, tool):
        """Test adding the same item multiple times."""
        user_id = "test_user_2"

        # Add item first time
        result1 = await tool.execute("add", user_id, product_id=1, quantity=1)
        assert result1["success"] is True

        # Add same item again
        result2 = await tool.execute("add", user_id, product_id=1, quantity=1)
        assert result2["success"] is True

        # Should have 2 items of the same product
        cart_item = result2["cart"][0]
        assert cart_item["product_id"] == 1
        assert cart_item["quantity"] == 2

    @pytest.mark.asyncio
    async def test_remove_from_cart(self, tool):
        """Test removing item from cart."""
        user_id = "test_user_3"

        # Add item first
        await tool.execute("add", user_id, product_id=1, quantity=1)

        # Remove item
        result = await tool.execute("remove", user_id, product_id=1)

        assert result["success"] is True
        assert result["total_items"] == 0

    @pytest.mark.asyncio
    async def test_clear_cart(self, tool):
        """Test clearing entire cart."""
        user_id = "test_user_4"

        # Add multiple items
        await tool.execute("add", user_id, product_id=1, quantity=1)
        await tool.execute("add", user_id, product_id=2, quantity=2)

        # Clear cart
        result = await tool.execute("clear", user_id)

        assert result["success"] is True
        assert result["total_items"] == 0
        assert len(result["cart"]) == 0

    @pytest.mark.asyncio
    async def test_invalid_action(self, tool):
        """Test invalid cart action."""
        result = await tool.execute("invalid_action", "test_user")

        assert result["success"] is False
        assert "error" in result


class TestOrderProcessingTool:
    """Test cases for the OrderProcessingTool class."""

    @pytest.fixture
    def tool(self):
        """Create an OrderProcessingTool instance for testing."""
        return OrderProcessingTool()

    @pytest.mark.asyncio
    async def test_create_order(self, tool):
        """Test creating an order."""
        result = await tool.execute(
            "create", "test_user", items=[{"product_id": 1, "quantity": 1}], total=99.99
        )

        assert result["success"] is True
        assert "order_id" in result
        assert result["status"] == "confirmed"
        assert result["order_id"].startswith("ORD-")

    @pytest.mark.asyncio
    async def test_get_order_status(self, tool):
        """Test getting order status."""
        # Create an order first
        create_result = await tool.execute(
            "create", "test_user", items=[{"product_id": 1, "quantity": 1}], total=99.99
        )
        order_id = create_result["order_id"]

        # Get order status
        result = await tool.execute("status", "test_user", order_id=order_id)

        assert result["success"] is True
        assert "order" in result
        assert result["order"]["order_id"] == order_id

    @pytest.mark.asyncio
    async def test_cancel_order(self, tool):
        """Test canceling an order."""
        # Create an order first
        create_result = await tool.execute(
            "create", "test_user", items=[{"product_id": 1, "quantity": 1}], total=99.99
        )
        order_id = create_result["order_id"]

        # Cancel the order
        result = await tool.execute("cancel", "test_user", order_id=order_id)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_invalid_order_operation(self, tool):
        """Test invalid order operation."""
        result = await tool.execute("invalid_action", "test_user")

        assert result["success"] is False
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__])
