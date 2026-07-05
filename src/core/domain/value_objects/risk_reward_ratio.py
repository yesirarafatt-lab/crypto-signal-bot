"""
Risk/reward ratio value object.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.core.domain.value_objects.price import Price
from src.core.exceptions.validation_exceptions import InvalidValueError


@dataclass(frozen=True, slots=True)
class RiskRewardRatio:
    """The ratio of potential reward to potential risk for a proposed trade."""

    value: Decimal

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise InvalidValueError(f"RiskRewardRatio must be positive, got {self.value}.")

    @classmethod
    def from_prices(cls, entry: Price, stop_loss: Price, target: Price) -> "RiskRewardRatio":
        """Derive the ratio from entry, stop-loss, and take-profit prices."""
        risk = abs(entry.amount - stop_loss.amount)
        reward = abs(target.amount - entry.amount)
        if risk == 0:
            raise InvalidValueError("Cannot compute risk/reward ratio when risk distance is zero.")
        return cls(reward / risk)

    def meets_minimum(self, minimum: "RiskRewardRatio") -> bool:
        """True if this ratio is at least as favorable as `minimum`."""
        return self.value >= minimum.value

    def __str__(self) -> str:
        return f"1:{self.value:.2f}"
