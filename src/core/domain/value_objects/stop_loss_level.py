"""
Stop-loss value object (price, basis).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.domain.value_objects.price import Price


class StopLossBasis(str, Enum):
    """The methodology used to derive a stop-loss level."""

    ATR = "atr"
    STRUCTURE = "structure"
    PERCENTAGE = "percentage"
    FIXED = "fixed"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class StopLossLevel:
    """A stop-loss price together with the methodology that produced it."""

    price: Price
    basis: StopLossBasis

    def distance_to(self, entry: Price) -> "Price":
        """The absolute price distance between `entry` and this stop-loss level."""
        return entry - self.price if entry.amount >= self.price.amount else self.price - entry

    def __str__(self) -> str:
        return f"SL({self.basis})={self.price}"
