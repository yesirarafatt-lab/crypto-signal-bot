"""
ABC for real-time liquidation event streaming.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import AsyncIterator, Sequence

from src.core.domain.entities.liquidation_event import LiquidationEvent
from src.core.domain.value_objects.symbol import Symbol


class LiquidationStream(ABC):
    """Contract for a real-time feed of forced-liquidation events, used for
    liquidation-cluster and cascade detection."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish the underlying stream connection. Must be idempotent."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the underlying stream connection and release its resources."""
        raise NotImplementedError

    @abstractmethod
    async def subscribe(self, symbols: Sequence[Symbol]) -> None:
        """Subscribe to liquidation events for `symbols`. Calling this again
        with a new set of symbols replaces the previous subscription."""
        raise NotImplementedError

    @abstractmethod
    def events(self) -> AsyncIterator[LiquidationEvent]:
        """An async iterator yielding liquidation events as they arrive.

        Must only be consumed after a successful `connect()` and `subscribe()`.
        """
        raise NotImplementedError

    async def __aenter__(self) -> "LiquidationStream":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.disconnect()
