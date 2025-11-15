"""Topic model - hierarchical categorization system."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Topic(BaseModel):
    """
    Hierarchical topic for categorizing events.
    Keep taxonomy small (~150 leaf topics) for manageability.
    """

    topic_id: Optional[str] = Field(
        default=None,
        description="Topic identifier, e.g. topic.economy.energy.oil or topic_economy_energy_oil",
    )
    path: List[str] = Field(
        default_factory=list,
        description="Hierarchical path: ['economy', 'energy', 'oil']",
    )
    aliases: List[str] = Field(
        default_factory=list, description="Keywords that map to this topic"
    )

    # Metadata
    description: Optional[str] = None
    parent_id: Optional[str] = Field(
        default=None, description="Parent topic ID for hierarchy navigation"
    )
    is_leaf: bool = Field(
        default=True, description="Whether this is a leaf topic (no children)"
    )

    # Statistics
    event_count: int = Field(default=0)
    last_refreshed: Optional[datetime] = Field(default=None)

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() + "Z"},
        extra="ignore",
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: List[str]) -> List[str]:
        """Ensure path components are valid."""
        if not value:
            raise ValueError("Topic path cannot be empty")
        for component in value:
            cleaned = component.replace("_", "").replace("-", "")
            if not cleaned.isalnum():
                raise ValueError(f"Invalid path component: {component}")
        return value

    @field_validator("aliases")
    @classmethod
    def normalize_aliases(cls, value: List[str]) -> List[str]:
        """Normalize alias list to unique, trimmed values."""
        if not value:
            return []
        normalized: List[str] = []
        seen = set()
        for alias in value:
            cleaned = alias.strip()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            normalized.append(cleaned)
        return normalized

    @model_validator(mode="after")
    def ensure_topic_id(self) -> "Topic":
        """Ensure topic_id is consistent with the path."""
        if not self.path:
            return self

        dot_notation = f"topic.{'.'.join(self.path)}"
        underscore_notation = f"topic_{'_'.join(self.path)}"

        if self.topic_id is None:
            self.topic_id = dot_notation
            return self

        if self.topic_id not in {dot_notation, underscore_notation}:
            raise ValueError(
                "topic_id must match the path (either topic.foo.bar or topic_foo_bar)"
            )
        return self

    @property
    def full_path(self) -> str:
        """Get the full path as a string."""
        return "/".join(self.path)
