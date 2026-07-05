"""
MarketType enum: SPOT, FUTURES.
"""

from __future__ import annotations

from enum import Enum


class MarketType(str, Enum):
    """The kind of market a symbol, order, or position belongs to."""

    SPOT = "spot"
    FUTURES = "futures"

    def __str__(self) -> str:
        return self.value
