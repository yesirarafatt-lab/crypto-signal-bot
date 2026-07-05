"""
Position size value object (units, notional, margin).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions.validation_exceptions import InvalidValueError


@dataclass(frozen=True, slots=True)
class PositionSize:
    """The sizing of a trade, as computed by the position-sizing service.

    `units` is the quantity of the base asset to trade, `notional` is that
    quantity's value in quote currency at the intended entry price, and
    `margin` is the account balance committed to open the position (equal to
    `notional` at 1x leverage, and smaller than `notional` under leverage).
    """

    units: float
    notional: float
    margin: float

    def __post_init__(self) -> None:
        if self.units <= 0:
            raise InvalidValueError(f"PositionSize units must be positive, got {self.units}.")
        if self.notional <= 0:
            raise InvalidValueError(
                f"PositionSize notional must be positive, got {self.notional}."
            )
        if self.margin <= 0:
            raise InvalidValueError(f"PositionSize margin must be positive, got {self.margin}.")
        if self.margin > self.notional:
            raise InvalidValueError(
                f"PositionSize margin ({self.margin}) cannot exceed notional "
                f"({self.notional}); leverage cannot be below 1x."
            )

    @property
    def leverage(self) -> float:
        """The implied leverage: notional value divided by margin committed."""
        return self.notional / self.margin

    def __str__(self) -> str:
        return (
            f"{self.units:g} units (notional={self.notional:.2f}, "
            f"margin={self.margin:.2f}, leverage={self.leverage:.2f}x)"
        )
