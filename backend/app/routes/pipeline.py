"""Endpoints for running world-model processing steps."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Literal, Mapping, Type

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

# Ensure the world_model package is importable when running without installation
ROOT_DIR = Path(__file__).resolve().parents[3]
WORLD_MODEL_SRC = ROOT_DIR / "world_model" / "src"
if WORLD_MODEL_SRC.exists():
    src_path = str(WORLD_MODEL_SRC)
    if src_path not in sys.path:
        sys.path.append(src_path)

from models import (  # type: ignore
    Entity,
    Event,
    PostingListShard,
    RawDocument,
    Topic,
)
from pipelines.normalizer import (  # type: ignore
    Normalizer,
)

from ..services import get_firestore_repository

router = APIRouter()

normalizer = Normalizer()
firestore_repo = get_firestore_repository()


class RawPayload(BaseModel):
    """Incoming raw payload prior to normalization."""

    data: Dict[str, Any]


class EventPayload(BaseModel):
    """Incoming event payload requiring validation."""

    data: Dict[str, Any]


class EntityPayload(BaseModel):
    """Incoming entity payload requiring validation."""

    data: Dict[str, Any]


class TopicPayload(BaseModel):
    """Incoming topic payload requiring validation."""

    data: Dict[str, Any]


class PostingListPayload(BaseModel):
    """Incoming posting list shard payload requiring validation."""

    data: Dict[str, Any]


@router.post("/normalize", response_model=RawDocument)
def normalize_document(payload: RawPayload) -> RawDocument:
    """Normalize raw input content to a RawDocument shape."""
    document = normalizer.normalize(payload.data)

    if firestore_repo.enabled:
        firestore_repo.upsert(
            collection="doc",
            document_id=document.doc_id,
            data=document.model_dump(exclude_none=True),
        )

    return document


@router.post("/events/validate", response_model=Event)
def validate_event(payload: EventPayload) -> Event:
    """Validate event payload and optionally persist to Firestore."""
    event = Event.model_validate(payload.data)

    if firestore_repo.enabled:
        firestore_repo.upsert(
            collection="event",
            document_id=event.event_id,
            data=event.model_dump(exclude_none=True),
        )

    return event


@router.post("/entities/validate", response_model=Entity)
def validate_entity(payload: EntityPayload) -> Entity:
    """Validate entity payload and optionally persist to Firestore."""
    entity = Entity.model_validate(payload.data)

    if firestore_repo.enabled:
        firestore_repo.upsert(
            collection="entity",
            document_id=entity.entity_id,
            data=entity.model_dump(exclude_none=True),
        )

    return entity


@router.post("/topics/validate", response_model=Topic)
def validate_topic(payload: TopicPayload) -> Topic:
    """Validate topic payload and optionally persist to Firestore."""
    topic = Topic.model_validate(payload.data)

    if firestore_repo.enabled:
        firestore_repo.upsert(
            collection="topic",
            document_id=topic.topic_id or topic.full_path,
            data=topic.model_dump(exclude_none=True),
        )

    return topic


@router.post("/indexes/validate", response_model=PostingListShard)
def validate_posting_list(payload: PostingListPayload) -> PostingListShard:
    """Validate posting list shard payload and optionally persist to Firestore."""
    shard = PostingListShard.model_validate(payload.data)

    if firestore_repo.enabled:
        firestore_repo.upsert(
            collection="posting_lists",
            document_id=shard.index_key,
            data=shard.model_dump(exclude_none=True),
        )

    return shard


class SchemaResponse(BaseModel):
    """Schema response payload."""

    model: Literal[
        "raw_document",
        "event",
        "entity",
        "topic",
        "posting_list",
    ]
    schema: Dict[str, Any]


SCHEMA_MAP: Mapping[str, Type[BaseModel]] = {
    "raw_document": RawDocument,
    "event": Event,
    "entity": Entity,
    "topic": Topic,
    "posting_list": PostingListShard,
}


@router.get("/schemas/{model_name}", response_model=SchemaResponse)
def get_schema(model_name: str) -> SchemaResponse:
    """Expose JSON schema for a particular model."""
    model = SCHEMA_MAP.get(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Unknown model '{model_name}'")

    return SchemaResponse(model=model_name, schema=model.model_json_schema())


@router.post("/validate/{model_name}")
def generic_validate(model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate arbitrary payloads against a named model.

    Useful for quick contract checks without a dedicated endpoint.
    """
    model = SCHEMA_MAP.get(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Unknown model '{model_name}'")

    try:
        instance = model.model_validate(payload)
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors()) from error

    return instance.model_dump(exclude_none=True)
