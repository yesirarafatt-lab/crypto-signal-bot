"""
ABC for position persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from src.core.domain.entities.position import Position


class PositionRepository(ABC):
    """Contract for persisting and querying trade positions."""

    @abstractmethod
    async def save(self, position: Position) -> Position:
        """Persist a new position, returning the saved instance."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, position: Position) -> Position:
        """Persist changes to an existing position (e.g. stop-loss move, close).

        Raises:
            EntityNotFoundError: if no position with this id exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, position_id: str) -> Position:
        """Return the position with `position_id`.

        Raises:
            EntityNotFoundError: if no such position exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_open_positions(self) -> Sequence[Position]:
        """Return all currently open positions."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_signal_id(self, signal_id: str) -> Position | None:
        """Return the position opened from `signal_id`, or None if none exists."""
        raise NotImplementedError
