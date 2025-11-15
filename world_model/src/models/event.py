"""Event model - core world model unit."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class Timespan(BaseModel):
    """Time range for an event."""

    start: datetime
    end: Optional[datetime] = None


class Where(BaseModel):
    """Geographic location information."""

    geo: Optional[str] = Field(default=None, description="Geographic identifier")
    iso2: Optional[str] = Field(
        default=None, description="ISO 3166-1 alpha-2 country code"
    )
    admin1: Optional[str] = Field(
        default=None, description="First-level admin division (state/province)"
    )
    place: Optional[str] = Field(
        default=None, description="Specific place name or venue"
    )
    s2: Optional[str] = Field(
        default=None, description="S2 cell token for coarse geospatial indexing"
    )
    coordinates: Optional[Dict[str, float]] = Field(
        default=None, description="Optional latitude/longitude coordinates"
    )


class StructuredClaim(BaseModel):
    """Structured representation of a claim."""

    actor: Optional[str] = Field(
        default=None, description="Actor entity id, e.g. ent_trump"
    )
    predicate: str = Field(
        description="Action/relationship type: policy_target_max_price, denial_of, etc."
    )
    object: Optional[str] = Field(
        default=None, description="Target entity id if the predicate expects one"
    )
    value: Optional[Dict[str, object]] = Field(
        default=None, description="Additional structured data like amounts or metadata"
    )
    modality: Optional[str] = Field(
        default=None,
        description="Mode of claim: said|proposed|announced|denied|confirmed",
    )
    temporal_scope: Optional[str] = Field(
        default=None, description="When the claim applies: immediate|future|past"
    )


class Claim(BaseModel):
    """A claim made in an event."""

    text: str = Field(description="Natural language claim text")
    structured: Optional[StructuredClaim] = Field(
        default=None, description="Structured extraction if successful"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in extraction accuracy",
    )


class Implication(BaseModel):
    """Downstream implication of an event."""

    category: str = Field(
        description="Impact category: markets/energy, politics/election, etc."
    )
    statement: str = Field(description="Description of the implication")
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence that the implication holds",
    )


class Event(BaseModel):
    """
    Core world model unit - something that happened/was said.
    Events aggregate related documents and extract structured information.
    """

    event_id: str = Field(description="Unique ID format: evt_{date}_{hash}")
    kind: Literal[
        "statement",
        "policy",
        "market_move",
        "conflict",
        "election",
        "legal",
        "macro",
        "tech_release",
        "other",
    ]
    timespan: Timespan
    where: Optional[Where] = None

    # Core content
    entities: List[str] = Field(
        default_factory=list, description="Entity IDs referenced in this event"
    )
    topics: List[str] = Field(
        default_factory=list, description="Topic IDs like topic.economy.energy.oil"
    )
    claims: List[Claim] = Field(
        default_factory=list, description="Extracted claims from this event"
    )
    implications: List[Implication] = Field(
        default_factory=list, description="Potential downstream effects"
    )

    # Provenance
    evidence_doc_ids: List[str] = Field(
        default_factory=list,
        description="Source document IDs supporting this event",
    )
    summary: Optional[str] = Field(
        default=None, description="Human-readable summary of the event"
    )
    source_reliability: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Optional source reliability score"
    )

    # Versioning
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() + "Z"},
        extra="ignore",
    )

    @field_validator("topics")
    @classmethod
    def validate_topics(cls, v: List[str]) -> List[str]:
        """Ensure topics follow hierarchical path format."""
        for topic in v:
            if not topic:
                raise ValueError("Topic IDs cannot be empty strings")
            segments = topic.split(".") if "topic." in topic else topic.split("/")
            for part in segments:
                stripped = part.replace("_", "").replace("-", "")
                if not stripped.isalnum():
                    raise ValueError(f"Invalid topic format: {topic}")
        return v

    @model_validator(mode="after")
    def ensure_claim_entities(self) -> "Event":
        """Ensure claim actors/objects are tracked in the entity list."""
        if self.claims:
            entities = list(self.entities)
            seen = set(entities)
            for claim in self.claims:
                structured = claim.structured
                if not structured:
                    continue
                if structured.actor and structured.actor not in seen:
                    entities.append(structured.actor)
                    seen.add(structured.actor)
                if structured.object and structured.object not in seen:
                    entities.append(structured.object)
                    seen.add(structured.object)
            self.entities = entities
        return self
