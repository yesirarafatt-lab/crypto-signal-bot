"""
SMC liquidity zone entity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.core.domain.value_objects.zone_range import ZoneRange


class LiquidityZoneType(str, Enum):
    """The kind of resting-liquidity pattern this zone represents."""

    EQUAL_HIGHS = "equal_highs"
    EQUAL_LOWS = "equal_lows"
    TRENDLINE_LIQUIDITY = "trendline_liquidity"
    SESSION_HIGH = "session_high"
    SESSION_LOW = "session_low"

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class LiquidityZone:
    """A price area where resting stop-loss/breakout orders are expected to
    cluster, and which price often "sweeps" before reversing."""

    symbol: Symbol
    timeframe: Timeframe
    zone: ZoneRange
    zone_type: LiquidityZoneType
    formed_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    swept: bool = False
    swept_at: datetime | None = None

    def mark_swept(self, at: datetime) -> None:
        """Mark this liquidity zone as swept (price has traded through and reversed)."""
        self.swept = True
        self.swept_at = at
