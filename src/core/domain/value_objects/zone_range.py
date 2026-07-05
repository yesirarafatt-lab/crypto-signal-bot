"""
ZoneRange value object (top/bottom) with overlap helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.core.domain.value_objects.price import Price
from src.core.exceptions.validation_exceptions import InvalidValueError


@dataclass(frozen=True, slots=True)
class ZoneRange:
    """A generic price band with a top and bottom bound, shared by entry zones,
    order blocks, fair value gaps, and liquidity zones."""

    top: Price
    bottom: Price

    def __post_init__(self) -> None:
        if self.bottom.amount > self.top.amount:
            raise InvalidValueError(
                f"ZoneRange bottom ({self.bottom}) cannot exceed top ({self.top})."
            )

    @property
    def midpoint(self) -> Price:
        """The price exactly halfway between top and bottom."""
        mid_amount = (self.top.amount + self.bottom.amount) / Decimal(2)
        return Price(mid_amount, precision=max(self.top.precision, self.bottom.precision))

    @property
    def height(self) -> Decimal:
        """The absolute price distance between top and bottom."""
        return self.top.amount - self.bottom.amount

    def contains(self, price: Price) -> bool:
        """True if `price` falls within [bottom, top], inclusive."""
        return self.bottom.amount <= price.amount <= self.top.amount

    def overlaps(self, other: "ZoneRange") -> bool:
        """True if this zone shares any price range with `other`."""
        return self.bottom.amount <= other.top.amount and other.bottom.amount <= self.top.amount

    def overlap_amount(self, other: "ZoneRange") -> Decimal:
        """The absolute size of the overlapping range with `other` (0 if none)."""
        overlap_top = min(self.top.amount, other.top.amount)
        overlap_bottom = max(self.bottom.amount, other.bottom.amount)
        return max(overlap_top - overlap_bottom, Decimal(0))

    def __str__(self) -> str:
        return f"[{self.bottom} - {self.top}]"
