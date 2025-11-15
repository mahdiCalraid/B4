"""API routes for file-based agents."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from agents.agent_loader import get_loader
from agents.general_codes.ai_model_selector import list_available_models, get_model_info


router = APIRouter(prefix="/agents", tags=["agents"])


class AgentRequest(BaseModel):
    """Request model for agent processing."""
    input: str
    provider: Optional[str] = None  # Deprecated: use 'model' instead
    model: Optional[str] = None  # Specific model to use (e.g., "gpt-4o", "gemini-2.0-flash")


class AgentResponse(BaseModel):
    """Response model for agent processing."""
    success: bool
    agent_id: str
    data: Dict[str, Any]
    provider: Optional[str] = None
    model: Optional[str] = None  # Actual model used


@router.get("/")
async def list_agents():
    """
    List all available agents.

    Returns:
        Dictionary of agent metadata
    """
    try:
        loader = get_loader()
        agents = loader.list_agents()

        return {
            "success": True,
            "count": len(agents),
            "agents": agents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}")
async def get_agent_info(agent_id: str):
    """
    Get information about a specific agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Agent metadata
    """
    try:
        loader = get_loader()
        info = loader.get_agent_info(agent_id)

        return {
            "success": True,
            "agent": info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}")
async def process_with_agent(
    agent_id: str,
    request: AgentRequest
) -> AgentResponse:
    """
    Process input with a specific agent.

    Args:
        agent_id: Agent identifier
        request: Request with input text and optional model/provider

    Returns:
        Processed result

    Example:
        {"input": "John went to Paris", "model": "gpt-4o"}
        {"input": "Extract people", "model": "gemini-2.0-flash"}
    """
    try:
        # Determine model to use (new 'model' param takes precedence)
        model_to_use = request.model or request.provider

        # Load agent with default provider (for fallback)
        loader = get_loader()
        agent = loader.load_agent(
            agent_id=agent_id,
            provider=request.provider if not request.model else None
        )

        # Process input with optional model override
        result = await agent.process(
            input_data=request.input,
            model=model_to_use
        )

        return AgentResponse(
            success=True,
            agent_id=agent_id,
            data=result,
            provider=request.provider,
            model=model_to_use or "gemini-2.0-flash-exp"
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/info")
async def get_detailed_info(agent_id: str):
    """
    Get detailed information about an agent including its loaded configuration.

    Args:
        agent_id: Agent identifier

    Returns:
        Detailed agent information
    """
    try:
        loader = get_loader()
        agent = loader.load_agent(agent_id)

        return {
            "success": True,
            "info": agent.get_info()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/list")
async def list_models(provider: Optional[str] = None):
    """
    List all available AI models.

    Args:
        provider: Optional filter by provider (gemini, openai, groq, ollama)

    Returns:
        Dictionary of available models with metadata
    """
    try:
        models = list_available_models(provider=provider)

        return {
            "success": True,
            "count": len(models),
            "models": models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_name}")
async def get_model_details(model_name: str):
    """
    Get details about a specific model.

    Args:
        model_name: Model name or alias

    Returns:
        Model information
    """
    try:
        info = get_model_info(model_name)

        return {
            "success": True,
            "model": info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
