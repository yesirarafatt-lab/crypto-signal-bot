"""
Swing high/low structure point entity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe


class StructurePointType(str, Enum):
    """Classification of a swing point relative to the preceding structure."""

    HIGHER_HIGH = "higher_high"
    HIGHER_LOW = "higher_low"
    LOWER_HIGH = "lower_high"
    LOWER_LOW = "lower_low"

    def __str__(self) -> str:
        return self.value

    @property
    def is_bullish(self) -> bool:
        """True for structure points that reinforce an uptrend (HH, HL)."""
        return self in (StructurePointType.HIGHER_HIGH, StructurePointType.HIGHER_LOW)


@dataclass(slots=True)
class MarketStructurePoint:
    """A confirmed swing high or swing low used as the foundation for SMC
    structure-break (BOS/CHoCH) detection."""

    symbol: Symbol
    timeframe: Timeframe
    price: Price
    point_type: StructurePointType
    timestamp: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
