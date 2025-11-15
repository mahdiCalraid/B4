"""Tool calling utilities for agents."""

from typing import Dict, Any, Callable, List, Optional
import inspect


class ToolRegistry:
    """Registry for agent tools."""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        func: Callable,
        description: str = "",
        parameters: Dict[str, Any] = None
    ):
        """
        Register a tool function.

        Args:
            name: Tool name
            func: Tool function
            description: Tool description
            parameters: Parameter schema
        """
        self.tools[name] = func

        # Extract metadata
        sig = inspect.signature(func)
        params = parameters or {
            param_name: {
                "type": param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "Any",
                "required": param.default == inspect.Parameter.empty
            }
            for param_name, param in sig.parameters.items()
        }

        self.tool_metadata[name] = {
            "name": name,
            "description": description or func.__doc__ or "",
            "parameters": params
        }

    def get_tool(self, name: str) -> Optional[Callable]:
        """Get tool function by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools."""
        return list(self.tool_metadata.values())

    async def call_tool(
        self,
        name: str,
        **kwargs
    ) -> Any:
        """
        Call a registered tool.

        Args:
            name: Tool name
            **kwargs: Tool parameters

        Returns:
            Tool result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")

        # Check if async
        if inspect.iscoroutinefunction(tool):
            return await tool(**kwargs)
        else:
            return tool(**kwargs)


# Global tool registry
_global_registry = ToolRegistry()


def register_tool(
    name: str,
    description: str = "",
    parameters: Dict[str, Any] = None
):
    """
    Decorator to register a tool.

    Example:
        @register_tool("extract_email", "Extract email from text")
        def extract_email(text: str) -> str:
            # implementation
            pass
    """
    def decorator(func: Callable):
        _global_registry.register(
            name=name,
            func=func,
            description=description,
            parameters=parameters
        )
        return func
    return decorator


def get_tool_registry() -> ToolRegistry:
    """Get global tool registry."""
    return _global_registry


async def call_tool(name: str, **kwargs) -> Any:
    """Call a tool from global registry."""
    return await _global_registry.call_tool(name, **kwargs)


def list_tools() -> List[Dict[str, Any]]:
    """List all available tools."""
    return _global_registry.list_tools()
