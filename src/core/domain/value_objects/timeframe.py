"""
Timeframe value object (1m..1d).
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from src.core.exceptions.validation_exceptions import InvalidValueError

_SECONDS_PER_UNIT: Final[dict[str, int]] = {"m": 60, "h": 3600, "d": 86400, "w": 604800}


class Timeframe(str, Enum):
    """A supported OHLCV candle interval, shared across strategies, indicators, and
    exchange OHLCV requests."""

    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    H6 = "6h"
    H8 = "8h"
    H12 = "12h"
    D1 = "1d"
    D3 = "3d"
    W1 = "1w"

    def __str__(self) -> str:
        return self.value

    @property
    def seconds(self) -> int:
        """Duration of one candle of this timeframe, in seconds."""
        unit = self.value[-1]
        amount = int(self.value[:-1])
        try:
            return amount * _SECONDS_PER_UNIT[unit]
        except KeyError as exc:
            raise InvalidValueError(f"Unrecognized timeframe unit in '{self.value}'.") from exc

    @classmethod
    def from_string(cls, value: str) -> "Timeframe":
        """Parse a raw string into a Timeframe, raising InvalidValueError if unsupported."""
        try:
            return cls(value)
        except ValueError as exc:
            valid = ", ".join(member.value for member in cls)
            raise InvalidValueError(
                f"Unsupported timeframe '{value}'. Valid values: {valid}."
            ) from exc

    def is_higher_than(self, other: "Timeframe") -> bool:
        """True if this timeframe spans a longer duration than `other`."""
        return self.seconds > other.seconds
