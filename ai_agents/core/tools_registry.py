"""
Tools registry for managing agent tools.
"""

from typing import Dict, List, Any, Callable, Optional
from abc import ABC, abstractmethod
import inspect


class BaseTool(ABC):
    """Base class for all agent tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema for LLM integration."""
        signature = inspect.signature(self.execute)
        parameters = {}

        for param_name, param in signature.parameters.items():
            if param_name not in ["self", "args", "kwargs"]:
                param_info = {
                    "type": "string",  # Default type
                    "description": f"Parameter {param_name}",
                }

                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == str:
                        param_info["type"] = "string"
                    elif param.annotation == int:
                        param_info["type"] = "integer"
                    elif param.annotation == float:
                        param_info["type"] = "number"
                    elif param.annotation == bool:
                        param_info["type"] = "boolean"

                if param.default != inspect.Parameter.empty:
                    param_info["default"] = param.default

                parameters[param_name] = param_info

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": [
                    name
                    for name, param in signature.parameters.items()
                    if param.default == inspect.Parameter.empty
                    and name not in ["self", "args", "kwargs"]
                ],
            },
        }


class ToolsRegistry:
    """Registry for managing and organizing agent tools."""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[str, List[str]] = {}

    def register_tool(self, tool: BaseTool, category: str = "general") -> None:
        """Register a new tool."""
        self.tools[tool.name] = tool

        if category not in self.categories:
            self.categories[category] = []

        if tool.name not in self.categories[category]:
            self.categories[category].append(tool.name)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a specific category."""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools."""
        return list(self.tools.values())

    def get_tool_schemas(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get schemas for tools, optionally filtered by category."""
        if category:
            tools = self.get_tools_by_category(category)
        else:
            tools = self.get_all_tools()

        return [tool.get_schema() for tool in tools]

    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        return tool.execute(*args, **kwargs)

    def list_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self.categories.keys())

    def list_tools(self) -> List[str]:
        """Get all tool names."""
        return list(self.tools.keys())

    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from the registry."""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            del self.tools[tool_name]

            # Remove from categories
            for category, tool_names in self.categories.items():
                if tool_name in tool_names:
                    tool_names.remove(tool_name)

            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_tools": len(self.tools),
            "categories": len(self.categories),
            "tools_by_category": {
                category: len(tool_names)
                for category, tool_names in self.categories.items()
            },
        }


# Global tools registry
global_tools_registry = ToolsRegistry()
