"""
Open trade position entity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.stop_loss_level import StopLossLevel
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.take_profit_level import TakeProfitLevel
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.core.exceptions.validation_exceptions import InvalidValueError


class PositionStatus(str, Enum):
    """The lifecycle state of a trade position."""

    OPEN = "open"
    CLOSED = "closed"

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class Position:
    """An open (or historically opened) trade position tracked for
    trailing-stop, break-even, and partial-take-profit management."""

    signal_id: str
    symbol: Symbol
    direction: TradeDecision
    entry_price: Price
    quantity: float
    stop_loss: StopLossLevel
    take_profits: list[TakeProfitLevel]
    opened_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: PositionStatus = PositionStatus.OPEN
    closed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.direction.is_actionable:
            raise InvalidValueError("A Position cannot be created with direction NO_TRADE.")
        if self.quantity <= 0:
            raise InvalidValueError(f"Position quantity must be positive, got {self.quantity}.")

    def update_stop_loss(self, new_stop_loss: StopLossLevel) -> None:
        """Replace the position's current stop-loss (e.g. trailing stop, break-even move)."""
        if self.status is not PositionStatus.OPEN:
            raise InvalidValueError(f"Cannot update stop-loss on a {self.status} position.")
        self.stop_loss = new_stop_loss

    def close(self, at: datetime) -> None:
        """Mark the position as closed."""
        if self.status is PositionStatus.CLOSED:
            raise InvalidValueError(f"Position '{self.id}' is already closed.")
        self.status = PositionStatus.CLOSED
        self.closed_at = at
