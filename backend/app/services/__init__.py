"""Service layer utilities for the backend."""

from .firestore import FirestoreRepository, get_firestore_repository

__all__ = ["FirestoreRepository", "get_firestore_repository"]
