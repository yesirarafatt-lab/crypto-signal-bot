"""
Closed trade result entity (pnl, r_multiple).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.trade_decision import TradeDecision


class ExitReason(str, Enum):
    """Why a position was closed."""

    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    BREAK_EVEN = "break_even"
    MANUAL = "manual"
    LIQUIDATION = "liquidation"

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class TradeResult:
    """The final outcome of a closed position: realized PnL and R-multiple,
    used for performance/statistics aggregation."""

    signal_id: str
    position_id: str
    symbol: Symbol
    direction: TradeDecision
    entry_price: Price
    exit_price: Price
    quantity: float
    pnl: float
    pnl_percent: float
    r_multiple: float
    exit_reason: ExitReason
    opened_at: datetime
    closed_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def is_win(self) -> bool:
        """True if the trade closed with positive realized PnL."""
        return self.pnl > 0

    @property
    def is_loss(self) -> bool:
        """True if the trade closed with negative realized PnL."""
        return self.pnl < 0
