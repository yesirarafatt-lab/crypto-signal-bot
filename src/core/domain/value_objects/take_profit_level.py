"""
Take-profit value object incl. partial size split.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.domain.value_objects.price import Price
from src.core.exceptions.validation_exceptions import OutOfRangeError


@dataclass(frozen=True, slots=True)
class TakeProfitLevel:
    """A single take-profit target within a (possibly multi-target) exit plan.

    `size_fraction` is the fraction of the total position closed at this
    level (e.g. 0.5 for TP1 closing half the position); across all levels in
    a signal's take-profit plan these should sum to 1.0.
    """

    price: Price
    size_fraction: float
    label: str = "TP1"

    def __post_init__(self) -> None:
        if not (0.0 < self.size_fraction <= 1.0):
            raise OutOfRangeError(
                f"TakeProfitLevel size_fraction must be within (0, 1], got {self.size_fraction}."
            )

    def __str__(self) -> str:
        return f"{self.label}={self.price} ({self.size_fraction:.0%})"
