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
secrets_env = Path(__file__).resolve().parents[2] / "secrets" / ".env"
if secrets_env.exists():
    load_dotenv(dotenv_path=secrets_env)
    print(f"✅ Loaded environment from {secrets_env}")
else:
    load_dotenv()
    print(f"⚠️  Using default .env (secrets/.env not found)")

# Ensure world_model source directory is on sys.path for local execution
ROOT_DIR = Path(__file__).resolve().parents[2]
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

