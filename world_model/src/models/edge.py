"""Edge model - relationships for graph traversal."""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class Edge(BaseModel):
    """
    Relationship between entities for 2-hop traversal.
    Stored in BigQuery for analytics (optional) or
    cached in hot_edges for frequently accessed relationships.
    """

    subj: str = Field(description="Subject entity ID")
    pred: str = Field(description="Predicate/relationship type")
    obj: str = Field(description="Object entity ID")

    # Temporal tracking
    first_seen: date
    last_seen: date

    # Strength
    weight: int = Field(
        default=1,
        ge=0,
        description="Relationship strength/frequency",
    )

    # Provenance
    evidence: List[str] = Field(
        default_factory=list, description="Event IDs supporting this edge"
    )

    # Optional attributes
    attributes: Dict[str, object] = Field(
        default_factory=dict, description="Additional edge-specific data"
    )

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat() + "Z",
        },
        extra="ignore",
    )

    @property
    def edge_id(self) -> str:
        """Generate unique edge identifier."""
        return f"{self.subj}:{self.pred}:{self.obj}"
