"""Entity model - canonical representation of actors, objects, concepts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntityType(str, Enum):
    """Types of entities we track."""

    PERSON = "Person"
    ORG = "Org"
    COMMODITY = "Commodity"
    COUNTRY = "Country"
    REGION = "Region"
    INSTRUMENT = "Instrument"  # Financial instruments
    CONCEPT = "Concept"  # Abstract concepts


class HotEdge(BaseModel):
    """
    Frequently accessed relationship to another entity.
    Cached for fast 2-hop traversal.
    """

    pred: str = Field(description="Predicate/relationship type")
    obj: str = Field(description="Object entity ID")
    weight: int = Field(ge=0, description="Strength/frequency of relationship")
    last: str = Field(description="Last seen date (YYYY-MM-DD)")


class Entity(BaseModel):
    """
    Canonical entity with aliases and relationships.
    Keep these small for fast retrieval.
    """

    entity_id: str = Field(description="Unique ID format: ent_{type}_{normalized_name}")
    type: EntityType
    name: str = Field(description="Canonical display name")
    aliases: List[str] = Field(
        default_factory=list, description="Alternative names/spellings"
    )

    # External references
    external: Dict[str, str] = Field(
        default_factory=dict, description="External IDs: wikidata, dbpedia, etc."
    )

    # Activity tracking
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)

    # Cached relationships (top N most important)
    hot_edges: List[HotEdge] = Field(
        default_factory=list,
        max_length=10,
        description="Top relationships cached for fast access",
    )

    # Statistics
    event_count: int = Field(
        default=0, description="Total events mentioning this entity"
    )

    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={datetime: lambda v: v.isoformat() + "Z"},
        extra="ignore",
    )

    @field_validator("aliases")
    @classmethod
    def normalize_aliases(cls, value: List[str]) -> List[str]:
        """Ensure aliases are trimmed and unique."""
        if not value:
            return []
        normalized: List[str] = []
        seen = set()
        for alias in value:
            if alias is None:
                continue
            cleaned = alias.strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            normalized.append(cleaned)
        return normalized
