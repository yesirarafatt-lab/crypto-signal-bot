"""
Persistence layer exception hierarchy.
"""

from __future__ import annotations


class RepositoryError(Exception):
    """Base class for all persistence-layer domain exceptions."""


class EntityNotFoundError(RepositoryError):
    """Raised when a requested entity does not exist in the underlying store."""


class DuplicateEntityError(RepositoryError):
    """Raised when an insert would violate a uniqueness constraint."""


class ConcurrencyConflictError(RepositoryError):
    """Raised when a write conflicts with a concurrent modification (optimistic locking)."""


class PersistenceError(RepositoryError):
    """Raised for unexpected persistence failures not covered by a more specific exception."""
