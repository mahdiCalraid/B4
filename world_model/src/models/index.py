"""Index models for Firestore posting lists."""

from __future__ import annotations

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PostingListShard(BaseModel):
    """
    Posting list shard for fast retrieval.
    Date-sharded (and optionally chunked) to keep documents small and predictable.
    """

    index_key: str = Field(
        description="Composite key such as entity_ent_trump_20250101 or topic_topic_energy_oil_20250101"
    )
    shard_date: date = Field(description="Date represented by this shard")
    chunk: int = Field(
        default=0,
        ge=0,
        description="Optional chunk counter if the daily list needs multiple docs",
    )
    event_ids: List[str] = Field(
        default_factory=list, description="Ordered list of event IDs"
    )
    count: int = Field(
        default=0,
        ge=0,
        description="Number of events (mirrors len(event_ids) for quick access)",
    )
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat() + "Z",
        },
        extra="ignore",
    )

    @model_validator(mode="after")
    def sync_count(self) -> "PostingListShard":
        """Ensure count mirrors the actual list length."""
        self.count = len(self.event_ids)
        return self

    @staticmethod
    def build_index_key(index_type: str, facet_id: str, shard_date: date, chunk: int = 0) -> str:
        """Generate a deterministic index key."""
        date_part = shard_date.strftime("%Y%m%d")
        base = f"{index_type}_{facet_id}_{date_part}"
        return f"{base}_{chunk}" if chunk else base
