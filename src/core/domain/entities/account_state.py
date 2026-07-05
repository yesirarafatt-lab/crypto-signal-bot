"""
Account equity/risk state entity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.core.exceptions.validation_exceptions import InvalidValueError


@dataclass(slots=True)
class AccountState:
    """A point-in-time snapshot of account equity and risk-tracking counters,
    consulted by the risk management services before approving new signals."""

    equity: float
    available_balance: float
    daily_pnl: float
    open_positions_count: int
    consecutive_losses: int
    updated_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cooldown_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.equity < 0:
            raise InvalidValueError(f"Account equity cannot be negative, got {self.equity}.")
        if self.available_balance < 0:
            raise InvalidValueError(
                f"Available balance cannot be negative, got {self.available_balance}."
            )
        if self.open_positions_count < 0:
            raise InvalidValueError(
                f"Open positions count cannot be negative, got {self.open_positions_count}."
            )
        if self.consecutive_losses < 0:
            raise InvalidValueError(
                f"Consecutive losses cannot be negative, got {self.consecutive_losses}."
            )

    @property
    def daily_pnl_percent(self) -> float:
        """Today's PnL as a percentage of current equity."""
        if self.equity == 0:
            return 0.0
        return (self.daily_pnl / self.equity) * 100

    def is_in_cooldown(self, as_of: datetime | None = None) -> bool:
        """True if a consecutive-loss cooldown is currently in effect as of `as_of`
        (defaults to now, using the cooldown timestamp's timezone)."""
        if self.cooldown_until is None:
            return False
        reference = as_of or datetime.now(self.cooldown_until.tzinfo)
        return reference < self.cooldown_until
