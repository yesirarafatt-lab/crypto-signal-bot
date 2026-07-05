"""
Funding rate entity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.domain.value_objects.symbol import Symbol


@dataclass(slots=True)
class FundingRate:
    """A perpetual futures funding rate snapshot for a symbol."""

    symbol: Symbol
    rate: float
    timestamp: datetime
    next_funding_time: datetime | None = None

    @property
    def is_positive(self) -> bool:
        """True if longs are paying shorts (bullish crowding signal)."""
        return self.rate > 0
