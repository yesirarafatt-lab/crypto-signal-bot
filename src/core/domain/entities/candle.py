"""
Candle (OHLCV) entity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.core.exceptions.validation_exceptions import InvalidValueError


@dataclass(slots=True)
class Candle:
    """A single OHLCV candle for a symbol/timeframe, as returned by market data
    providers. Prices/volume are kept as raw floats (mirroring exchange data);
    domain-level computed prices use the `Price` value object instead."""

    symbol: Symbol
    timeframe: Timeframe
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        if self.high < self.low:
            raise InvalidValueError(
                f"Candle high ({self.high}) cannot be below low ({self.low})."
            )
        if not (self.low <= self.open <= self.high):
            raise InvalidValueError(
                f"Candle open ({self.open}) must lie between low ({self.low}) and "
                f"high ({self.high})."
            )
        if not (self.low <= self.close <= self.high):
            raise InvalidValueError(
                f"Candle close ({self.close}) must lie between low ({self.low}) and "
                f"high ({self.high})."
            )
        if self.volume < 0:
            raise InvalidValueError(f"Candle volume cannot be negative, got {self.volume}.")

    @property
    def is_bullish(self) -> bool:
        """True if the candle closed above where it opened."""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """True if the candle closed below where it opened."""
        return self.close < self.open

    @property
    def body_size(self) -> float:
        """Absolute size of the candle body (|close - open|)."""
        return abs(self.close - self.open)

    @property
    def range_size(self) -> float:
        """Absolute size of the full candle range (high - low)."""
        return self.high - self.low
