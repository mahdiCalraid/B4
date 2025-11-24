"""FastAPI entry point for the world model backend."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import get_api_router

# Try to import firestore, but make it optional
try:
    from .services import get_firestore_repository
    FIRESTORE_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Firestore not available: {e}")
    FIRESTORE_AVAILABLE = False
    def get_firestore_repository():
        class DummyRepo:
            enabled = False
        return DummyRepo()

# Load environment variables early
# Try to load from secrets/.env first, then fall back to default .env
# Use override=True to ensure secrets/.env takes precedence over shell env vars
secrets_env = Path(__file__).resolve().parents[2] / "secrets" / ".env"
if secrets_env.exists():
    load_dotenv(dotenv_path=secrets_env, override=True)
    print(f"✅ Loaded environment from {secrets_env} (with override)")
else:
    load_dotenv(override=True)
    print(f"⚠️  Using default .env (secrets/.env not found)")

# Ensure world_model source directory is on sys.path for local execution
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

WORLD_MODEL_SRC = ROOT_DIR / "world_model" / "src"
if WORLD_MODEL_SRC.exists() and str(WORLD_MODEL_SRC) not in sys.path:
    sys.path.append(str(WORLD_MODEL_SRC))

app = FastAPI(
    title="World Model Backend",
    description="Validation and persistence service for the world model pipeline",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(get_api_router())

@app.get("/api/traces")
async def get_traces() -> dict:
    """Get all recorded traces."""
    from modules.base import TRACE_STORE
    
    # Return summary of traces (id, timestamp, first input)
    summaries = []
    for trace_id, steps in TRACE_STORE.items():
        if not steps:
            continue
        first_step = steps[0]
        summaries.append({
            "trace_id": trace_id,
            "timestamp": first_step.timestamp,
            "input_preview": str(first_step.input_data.get("text", ""))[:50],
            "step_count": len(steps)
        })
    
    # Sort by timestamp desc
    summaries.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"traces": summaries}

@app.get("/api/traces/{trace_id}")
async def get_trace_detail(trace_id: str) -> dict:
    """Get detailed steps for a specific trace."""
    from modules.base import TRACE_STORE
    
    if trace_id not in TRACE_STORE:
        return {"error": "Trace not found"}
        
    return {
        "trace_id": trace_id,
        "steps": [step.to_dict() for step in TRACE_STORE[trace_id]]
    }

@app.get("/api/nodes")
async def get_nodes() -> dict:
    """Get all available nodes (Agents, Connectors, Logic)."""
    from registry import registry
    
    # Refresh registry on request (for dev mode)
    registry.scan_all()
    
    return {
        "nodes": registry.list_nodes()
    }

@app.post("/api/workflows/execute")
async def execute_workflow(workflow: dict) -> dict:
    """Execute a workflow."""
    from engine import engine
    execution_id = await engine.execute_workflow(workflow)
    return {"execution_id": execution_id, "status": "started"}

@app.get("/api/execution/{execution_id}/status")
async def get_execution_status(execution_id: str) -> dict:
    """Get status of an execution."""
    from engine import engine
    
    context = engine.executions.get(execution_id)
    if not context:
        return {"error": "Execution not found"}
        
    return {
        "execution_id": execution_id,
        "state": context.state,
        "error": getattr(context, "error", None),
        "outputs": context.node_outputs,
        "logs": getattr(context, "logs", [])
    }

@app.get("/api/workflows")
async def list_workflows() -> dict:
    """List all available workflows."""
    from workflow_store import workflow_store
    return {"workflows": workflow_store.list_workflows()}

@app.post("/api/workflows")
async def save_workflow(workflow: dict) -> dict:
    """Save a workflow."""
    from workflow_store import workflow_store
    workflow_id = workflow_store.save_workflow(workflow)
    return {"id": workflow_id, "status": "saved"}

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> dict:
    """Get a specific workflow."""
    from workflow_store import workflow_store
    workflow = workflow_store.get_workflow(workflow_id)
    if not workflow:
        return {"error": "Workflow not found"}
    return workflow


@app.get("/")
async def root() -> dict:
    """Root endpoint with basic service metadata."""
    from modules.registry import registry

    return {
        "service": "world-model-backend",
        "version": app.version,
        "status": "running",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules_loaded": registry.get_module_count(),
        "endpoints": {
            "health": "/health",
            "pipeline": "/pipeline/*",
            "modules": "/api/modules/",
            "chat": "/api/modules/chat",
        },
    }


@app.get("/health")
async def health() -> dict:
    """Health endpoint for Cloud Run probes."""
    firestore_repo = get_firestore_repository()
    return {
        "status": "healthy",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "firestore_writes_enabled": firestore_repo.enabled,
        "gcp_project": settings.gcp_project,
    }


@app.on_event("startup")
async def on_startup() -> None:
    """Log startup information."""
    from .startup import startup

    print("\n" + "=" * 70)
    print("🚀 World Model Backend Starting")
    print("=" * 70)
    print(f"Environment: {settings.environment}")
    print(f"GCP Project: {settings.gcp_project}")
    print(f"Firestore Writes Enabled: {get_firestore_repository().enabled}")
    print(f"Listening Port: {settings.port}")
    print("=" * 70 + "\n")

    # Register modules
    startup()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", settings.port))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )

