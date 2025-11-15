"""Firestore persistence helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import Client
from loguru import logger

from ..config import settings


class FirestoreRepository:
    """Thin wrapper around Firestore client with optional activation."""

    def __init__(self, client: Optional[Client] = None) -> None:
        self._client = client

    @property
    def enabled(self) -> bool:
        """Whether Firestore writes are available."""
        return self._client is not None

    def _require_client(self) -> Client:
        if not self._client:
            raise RuntimeError("Firestore client not initialized (ENABLE_FIRESTORE_WRITES disabled).")
        return self._client

    def upsert(self, collection: str, document_id: str, data: Dict[str, Any]) -> None:
        """Upsert data into a collection/document id."""
        client = self._require_client()
        logger.debug("Upserting document", collection=collection, document_id=document_id)
        client.collection(collection).document(document_id).set(data, merge=True)

    def delete(self, collection: str, document_id: str) -> None:
        """Delete a document if Firestore is enabled."""
        client = self._require_client()
        logger.debug("Deleting document", collection=collection, document_id=document_id)
        client.collection(collection).document(document_id).delete()


def _create_client() -> Optional[Client]:
    """Instantiate Firestore client based on settings."""
    if not settings.enable_firestore_writes:
        logger.info("Firestore writes disabled via ENABLE_FIRESTORE_WRITES; running in dry-run mode.")
        return None

    project_id = settings.firestore_project_id
    if not project_id:
        logger.warning(
            "Firestore writes requested but no project id configured; falling back to dry-run mode."
        )
        return None

    logger.info("Initializing Firestore client", project_id=project_id)
    try:
        return firestore.Client(project=project_id)
    except Exception as exc:  # pragma: no cover - runtime guard
        logger.exception("Failed to initialize Firestore client", exc=exc)
        return None


_repository: Optional[FirestoreRepository] = None


def get_firestore_repository() -> FirestoreRepository:
    """Return singleton repository instance."""
    global _repository
    if _repository is None:
        _repository = FirestoreRepository(client=_create_client())
    return _repository
