"""
SMC fair value gap entity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.core.domain.value_objects.zone_range import ZoneRange


@dataclass(slots=True)
class FairValueGap:
    """A three-candle imbalance (gap between candle 1's wick and candle 3's
    wick) left by a displacement move, which price tends to revisit ("fill")."""

    symbol: Symbol
    timeframe: Timeframe
    zone: ZoneRange
    direction: TradeDecision
    formed_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filled: bool = False
    filled_at: datetime | None = None

    def mark_filled(self, at: datetime) -> None:
        """Mark this fair value gap as filled (price has fully traded through it)."""
        self.filled = True
        self.filled_at = at
