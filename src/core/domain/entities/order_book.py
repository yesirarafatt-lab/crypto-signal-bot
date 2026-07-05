"""
Order book snapshot entity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.domain.value_objects.symbol import Symbol

# Each level is a (price, quantity) pair, ordered best-to-worst.
OrderBookLevel = tuple[float, float]


@dataclass(slots=True)
class OrderBook:
    """A point-in-time order book snapshot for a symbol."""

    symbol: Symbol
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: datetime

    @property
    def best_bid(self) -> OrderBookLevel | None:
        """The highest bid level, or None if the book side is empty."""
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> OrderBookLevel | None:
        """The lowest ask level, or None if the book side is empty."""
        return self.asks[0] if self.asks else None

    @property
    def spread(self) -> float | None:
        """The best-ask minus best-bid spread, or None if either side is empty."""
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask[0] - self.best_bid[0]

    @property
    def mid_price(self) -> float | None:
        """The midpoint between best bid and best ask, or None if either side is empty."""
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid[0] + self.best_ask[0]) / 2
