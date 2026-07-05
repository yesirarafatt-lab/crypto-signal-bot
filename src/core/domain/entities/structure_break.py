"""
BOS / CHoCH event entity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.domain.entities.market_structure_point import MarketStructurePoint
from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.core.domain.value_objects.trade_decision import TradeDecision


class StructureBreakType(str, Enum):
    """Break of Structure (trend continuation) vs Change of Character (reversal)."""

    BOS = "bos"
    CHOCH = "choch"

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class StructureBreak:
    """A Break-of-Structure or Change-of-Character event: price closing beyond
    a previously confirmed swing point, signalling continuation or reversal."""

    symbol: Symbol
    timeframe: Timeframe
    break_type: StructureBreakType
    direction: TradeDecision
    break_price: Price
    broken_point: MarketStructurePoint
    timestamp: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
