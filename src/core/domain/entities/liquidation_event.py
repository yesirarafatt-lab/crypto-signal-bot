"""
Liquidation event entity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.trade_decision import TradeDecision


@dataclass(slots=True)
class LiquidationEvent:
    """A single forced-liquidation event streamed from an exchange, used for
    liquidation-cluster and cascade detection."""

    symbol: Symbol
    side: TradeDecision
    price: float
    quantity: float
    timestamp: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def notional_value(self) -> float:
        """The approximate USD (or quote-currency) value of the liquidated position."""
        return self.price * self.quantity
