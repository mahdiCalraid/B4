"""Module router for intelligent request routing."""

from typing import Dict, Any
from .registry import registry


class ModuleRouter:
    """
    Routes requests to appropriate modules based on content or explicit selection.
    """

    def __init__(self):
        self.registry = registry

    async def route(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to appropriate module based on content.

        Args:
            request_data: Dictionary with:
                - text: str (user message/input)
                - user_id: str (optional)
                - module: str (optional, explicit module name)
                - params: dict (optional, additional parameters)

        Returns:
            Module processing result
        """
        import uuid
        from .base import add_trace_step, update_trace_step

        # Generate or retrieve trace_id
        trace_id = request_data.get("trace_id")
        if not trace_id:
            trace_id = str(uuid.uuid4())
            request_data["trace_id"] = trace_id

        # Record Router Entry
        add_trace_step(trace_id, "Router", request_data)

        try:
            # Explicit module specified
            if "module" in request_data and request_data["module"]:
                module_name = request_data["module"]
                module = self.registry.get_module(module_name)
                
                # Record Module Entry
                add_trace_step(trace_id, module_name, request_data)
                result = await module.process(request_data)
                update_trace_step(trace_id, module_name, result)
                
                # Update Router Exit
                update_trace_step(trace_id, "Router", result)
                return result

            # Infer module from content
            module_name = self._infer_module(request_data)
            module = self.registry.get_module(module_name)

            # Record Module Entry
            add_trace_step(trace_id, module_name, request_data)
            result = await module.process(request_data)
            update_trace_step(trace_id, module_name, result)

            # Update Router Exit
            update_trace_step(trace_id, "Router", result)
            return result
            
        except Exception as e:
            error_result = {"error": str(e)}
            update_trace_step(trace_id, "Router", error_result)
            raise e

    def _infer_module(self, request_data: Dict[str, Any]) -> str:
        """
        Infer which module should handle this request.

        Simple keyword-based routing for now. Can be replaced with
        a classifier module later for smarter routing.

        Args:
            request_data: Request data to analyze

        Returns:
            Module name to use
        """
        text = request_data.get("text", "").lower()

        # Keyword-based routing rules
        routing_rules = [
            (["analyze", "analysis", "what happened", "explain", "insight"],
             "AnalyzerModule"),
            (["classify", "category", "type", "kind", "what is this"],
             "ClassifierModule"),
            (["hello", "hi", "hey", "help"], "ChatAgentModule"),
        ]

        for keywords, module_name in routing_rules:
            if any(keyword in text for keyword in keywords):
                if self.registry.module_exists(module_name):
                    return module_name

        # Default to chat agent if available
        if self.registry.module_exists("ChatAgentModule"):
            return "ChatAgentModule"

        # Fallback to first available module
        modules = self.registry.list_modules()
        if modules:
            return list(modules.keys())[0]

        raise ValueError("No modules available for routing")


# Global router instance
router = ModuleRouter()
