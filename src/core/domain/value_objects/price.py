"""
Price value object with precision handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from src.core.exceptions.validation_exceptions import InvalidValueError

_DEFAULT_PRECISION = 8


def _to_decimal(value: Decimal | float | int | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


@dataclass(frozen=True, slots=True)
class Price:
    """An immutable monetary price with explicit decimal precision.

    Stored internally as `Decimal` to avoid binary floating-point drift in
    price/PnL arithmetic. `precision` controls display and quantization, not
    the stored value's internal accuracy.
    """

    amount: Decimal
    precision: int = _DEFAULT_PRECISION

    def __init__(
        self, amount: Decimal | float | int | str, precision: int = _DEFAULT_PRECISION
    ) -> None:
        decimal_amount = _to_decimal(amount)
        if decimal_amount <= 0:
            raise InvalidValueError(f"Price must be strictly positive, got {decimal_amount}.")
        if precision < 0:
            raise InvalidValueError(f"Precision must be >= 0, got {precision}.")
        object.__setattr__(self, "amount", decimal_amount)
        object.__setattr__(self, "precision", precision)

    def quantized(self) -> Decimal:
        """Return the amount rounded to `precision` decimal places."""
        exponent = Decimal(1).scaleb(-self.precision)
        return self.amount.quantize(exponent, rounding=ROUND_HALF_UP)

    def as_float(self) -> float:
        """Return the quantized amount as a float, for interop with numeric libraries."""
        return float(self.quantized())

    def percent_difference(self, other: "Price") -> Decimal:
        """Percentage difference of `other` relative to this price: (other - self) / self * 100."""
        return (other.amount - self.amount) / self.amount * Decimal(100)

    def __add__(self, other: "Price") -> "Price":
        return Price(self.amount + other.amount, precision=max(self.precision, other.precision))

    def __sub__(self, other: "Price") -> "Price":
        return Price(self.amount - other.amount, precision=max(self.precision, other.precision))

    def __lt__(self, other: "Price") -> bool:
        return self.amount < other.amount

    def __le__(self, other: "Price") -> bool:
        return self.amount <= other.amount

    def __gt__(self, other: "Price") -> bool:
        return self.amount > other.amount

    def __ge__(self, other: "Price") -> bool:
        return self.amount >= other.amount

    def __str__(self) -> str:
        return str(self.quantized())
