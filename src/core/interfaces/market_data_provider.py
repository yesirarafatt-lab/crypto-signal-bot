"""
ABC for OHLCV/funding/OI/order book/volume retrieval.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class MarketDataProvider(ABC):
    """Contract for read-only market data retrieval from an exchange."""

    @abstractmethod
    async def fetch_ticker(self, symbol: str) -> Mapping[str, Any]:
        """Fetch the current ticker (last price, bid/ask, 24h stats) for `symbol`."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: int | None = None,
        limit: int | None = None,
    ) -> Sequence[Sequence[float]]:
        """Fetch OHLCV candles for `symbol` at the given `timeframe`.

        Returns a sequence of ``[timestamp, open, high, low, close, volume]`` rows.
        """
        raise NotImplementedError
