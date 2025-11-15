"""Raw Document model - immutable source records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class MediaItem(BaseModel):
    """Media attachment in a document."""

    type: str = Field(description="Media type: image, video, audio")
    url: HttpUrl
    alt_text: Optional[str] = None


class RawDocument(BaseModel):
    """
    Immutable raw document from any source.
    This is the ground truth that everything else derives from.
    """

    doc_id: str = Field(description="Unique ID format: src_{source}_{timestamp}_{hash}")
    source: Literal[
        "x", "reddit", "news", "email", "telegram", "linkedin", "forum", "unknown"
    ] = Field(description="Source platform identifier")
    url: Optional[HttpUrl] = None
    author_handle: Optional[str] = None
    author_name: Optional[str] = None
    published_at: Optional[datetime] = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    lang: Optional[str] = Field(default="en")
    title: Optional[str] = None
    body: Optional[str] = Field(
        default=None, description="Full normalized text content (if accessible)"
    )
    media: List[MediaItem] = Field(
        default_factory=list, description="Structured media attachments"
    )
    checksum: Optional[str] = Field(
        default=None, description="SHA256 hash of content for deduplication"
    )
    simhash: Optional[str] = Field(
        default=None, description="Optional simhash/minhash fingerprint"
    )
    gcs_uri: Optional[str] = Field(
        default=None, description="Pointer to raw payload in Cloud Storage"
    )
    length_chars: Optional[int] = Field(
        default=None, ge=0, description="Character length of the normalized body"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional platform-specific metadata",
    )

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat() + "Z"},
        extra="ignore",
    )

    @model_validator(mode="after")
    def set_length(self) -> "RawDocument":
        """Populate length if a body is present."""
        if self.body is not None and self.length_chars is None:
            self.length_chars = len(self.body)
        return self
