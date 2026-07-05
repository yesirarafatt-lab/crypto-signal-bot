"""
SMC order block entity.
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
class OrderBlock:
    """A candle (or cluster of candles) whose range represents the last
    opposing-direction move before a displacement, marking an institutional
    supply/demand zone that price may return to and react from."""

    symbol: Symbol
    timeframe: Timeframe
    zone: ZoneRange
    direction: TradeDecision
    formed_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mitigated: bool = False
    mitigated_at: datetime | None = None

    def mark_mitigated(self, at: datetime) -> None:
        """Mark this order block as mitigated (price has traded back through it)."""
        self.mitigated = True
        self.mitigated_at = at
