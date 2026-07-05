"""
ABC for signal persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from src.core.domain.entities.signal import Signal, SignalStatus
from src.core.domain.value_objects.symbol import Symbol


class SignalRepository(ABC):
    """Contract for persisting and querying generated trading signals."""

    @abstractmethod
    async def save(self, signal: Signal) -> Signal:
        """Persist a new signal, returning the saved instance."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, signal: Signal) -> Signal:
        """Persist changes to an existing signal (e.g. a status transition).

        Raises:
            EntityNotFoundError: if no signal with this id exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, signal_id: str) -> Signal:
        """Return the signal with `signal_id`.

        Raises:
            EntityNotFoundError: if no such signal exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_open_signals(self, symbol: Symbol | None = None) -> Sequence[Signal]:
        """Return all signals with an open status (PENDING/ACTIVE), optionally
        filtered to a single `symbol`."""
        raise NotImplementedError

    @abstractmethod
    async def get_history(
        self,
        symbol: Symbol | None = None,
        status: SignalStatus | None = None,
        since: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Signal]:
        """Return past signals, most recent first, filtered by any combination
        of `symbol`, `status`, and `since`, paginated by `limit`/`offset`."""
        raise NotImplementedError
