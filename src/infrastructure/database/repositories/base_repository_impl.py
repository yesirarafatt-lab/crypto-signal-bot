"""
Repository implementation: base.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.repository_exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    PersistenceError,
)
from src.infrastructure.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Shared SQLAlchemy plumbing reused by every concrete repository
    implementation: session handling, id lookups, and translation of
    low-level SQLAlchemy errors into the `core.exceptions.repository_exceptions`
    hierarchy so the application layer never depends on SQLAlchemy directly.
    """

    model_type: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_model_by_id(self, entity_id: str) -> ModelT:
        """Fetch a row by primary key, raising `EntityNotFoundError` if absent."""
        model = await self._session.get(self.model_type, entity_id)
        if model is None:
            raise EntityNotFoundError(
                f"{self.model_type.__name__} with id '{entity_id}' was not found."
            )
        return model

    async def _flush(self) -> None:
        """Flush pending changes to the database within the current
        transaction, translating constraint violations into domain
        exceptions. Does not commit; the caller's `UnitOfWork` or session
        dependency owns the transaction boundary.
        """
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise DuplicateEntityError(
                f"A {self.model_type.__name__} violating a uniqueness constraint already exists."
            ) from exc
        except Exception as exc:  # noqa: BLE001 - never leak raw driver errors upward.
            raise PersistenceError(
                f"Unexpected persistence failure for {self.model_type.__name__}: {exc}"
            ) from exc
