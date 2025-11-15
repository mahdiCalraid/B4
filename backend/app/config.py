"""Application configuration using pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Configuration values loaded from environment variables."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"  # Allow extra fields from .env (like API keys)
    )

    environment: str = Field(default="production", alias="ENVIRONMENT")
    port: int = Field(default=8080, alias="PORT")

    gcp_project: Optional[str] = Field(
        default="bthree-476203",
        alias="GOOGLE_CLOUD_PROJECT",
        description="Google Cloud project id used for Cloud Run / Firestore",
    )
    firestore_project: Optional[str] = Field(
        default=None,
        alias="FIRESTORE_PROJECT_ID",
        description="Explicit Firestore project id (defaults to gcp_project when unset)",
    )
    enable_firestore_writes: bool = Field(
        default=False,
        alias="ENABLE_FIRESTORE_WRITES",
        description="Enable Firestore persistence when True",
    )

    @property
    def firestore_project_id(self) -> Optional[str]:
        """Return the Firestore project id to use."""
        return self.firestore_project or self.gcp_project


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()

