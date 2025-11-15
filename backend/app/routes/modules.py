"""API routes for module operations."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from modules.registry import registry
from modules.router import router as module_router


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    text: str = Field(..., description="Input text to process")
    user_id: Optional[str] = Field(None, description="User identifier")
    module: Optional[str] = Field(None, description="Specific module to use")
    params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class ModuleProcessRequest(BaseModel):
    """Request model for direct module processing."""
    text: str = Field(..., description="Input text to process")
    user_id: Optional[str] = Field(None, description="User identifier")
    params: Optional[Dict[str, Any]] = Field(None, description="Module-specific parameters")


# Create router
modules_router = APIRouter(prefix="/modules", tags=["Modules"])


@modules_router.get("/")
async def list_modules() -> Dict[str, Any]:
    """
    List all available modules.

    Returns:
        Dictionary with module information
    """
    modules = registry.list_modules()

    return {
        "count": len(modules),
        "modules": modules
    }


@modules_router.get("/{module_name}")
async def get_module_info(module_name: str) -> Dict[str, Any]:
    """
    Get information about a specific module.

    Args:
        module_name: Name of the module

    Returns:
        Module information

    Raises:
        HTTPException: If module not found
    """
    try:
        module = registry.get_module(module_name)
        info = module.get_info()
        is_healthy = await module.health_check()

        return {
            **info,
            "healthy": is_healthy
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@modules_router.post("/{module_name}/process")
async def process_with_module(
    module_name: str,
    request: ModuleProcessRequest
) -> Dict[str, Any]:
    """
    Process input with a specific module.

    Args:
        module_name: Name of the module to use
        request: Request data

    Returns:
        Processing result

    Raises:
        HTTPException: If module not found or processing fails
    """
    try:
        module = registry.get_module(module_name)

        input_data = {
            "text": request.text,
            "user_id": request.user_id,
            "params": request.params or {}
        }

        result = await module.process(input_data)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@modules_router.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Send a message and let the router determine which module to use.

    This endpoint intelligently routes to the appropriate module based on
    the input text, unless a specific module is requested.

    Args:
        request: Chat request with text and optional module

    Returns:
        Processing result from the selected module
    """
    try:
        input_data = {
            "text": request.text,
            "user_id": request.user_id,
            "module": request.module,
            "params": request.params or {}
        }

        result = await module_router.route(input_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")


# Create API router that includes modules
api_router = APIRouter(prefix="/api")
api_router.include_router(modules_router)
