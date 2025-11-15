"""Router package for FastAPI endpoints."""

from fastapi import APIRouter

# Import modules router (always works)
from .modules import api_router as modules_api_router

# Import agents router
try:
    from .agents import router as agents_router
    AGENTS_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Agents router not available: {e}")
    AGENTS_AVAILABLE = False
    agents_router = None

# Try to import pipeline router (may have dependencies issues)
try:
    from .pipeline import router as pipeline_router
    PIPELINE_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Pipeline router not available: {e}")
    PIPELINE_AVAILABLE = False
    pipeline_router = None


def get_api_router() -> APIRouter:
    """Aggregate application routers."""
    api = APIRouter()

    # Always include modules router
    api.include_router(modules_api_router, tags=["modules"])

    # Include agents router if available
    if AGENTS_AVAILABLE and agents_router:
        api.include_router(agents_router, tags=["agents"])

    # Include pipeline router only if available
    if PIPELINE_AVAILABLE and pipeline_router:
        api.include_router(pipeline_router, prefix="/pipeline", tags=["world-model"])

    return api


__all__ = ["get_api_router"]
