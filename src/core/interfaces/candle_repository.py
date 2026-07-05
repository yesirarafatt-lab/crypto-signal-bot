"""
ABC for candle persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from src.core.domain.entities.candle import Candle
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe


class CandleRepository(ABC):
    """Contract for persisting and querying OHLCV candle history."""

    @abstractmethod
    async def save(self, candle: Candle) -> None:
        """Persist a single candle, upserting on (symbol, timeframe, timestamp)."""
        raise NotImplementedError

    @abstractmethod
    async def save_many(self, candles: Sequence[Candle]) -> None:
        """Persist multiple candles in a single batch, upserting duplicates."""
        raise NotImplementedError

    @abstractmethod
    async def get_latest(
        self, symbol: Symbol, timeframe: Timeframe, limit: int = 200
    ) -> Sequence[Candle]:
        """Return up to `limit` most recent candles for `symbol`/`timeframe`,
        ordered oldest to newest."""
        raise NotImplementedError

    @abstractmethod
    async def get_range(
        self, symbol: Symbol, timeframe: Timeframe, start: datetime, end: datetime
    ) -> Sequence[Candle]:
        """Return all candles for `symbol`/`timeframe` within [start, end],
        ordered oldest to newest."""
        raise NotImplementedError

    @abstractmethod
    async def delete_older_than(self, cutoff: datetime) -> int:
        """Delete all candles older than `cutoff`, returning the number deleted."""
        raise NotImplementedError
