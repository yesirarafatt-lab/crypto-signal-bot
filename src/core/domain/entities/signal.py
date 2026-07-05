"""
Signal entity — direction, entry zone, SL/TP, confidence, risk score, reasoning.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.domain.value_objects.confidence_score import ConfidenceScore
from src.core.domain.value_objects.entry_zone import EntryZone
from src.core.domain.value_objects.risk_reward_ratio import RiskRewardRatio
from src.core.domain.value_objects.risk_score import RiskScore
from src.core.domain.value_objects.signal_strength import SignalStrength
from src.core.domain.value_objects.stop_loss_level import StopLossLevel
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.take_profit_level import TakeProfitLevel
from src.core.domain.value_objects.timeframe import Timeframe
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.core.exceptions.signal_exceptions import InvalidSignalError


class SignalStatus(str, Enum):
    """The lifecycle state of a generated trading signal."""

    PENDING = "pending"
    ACTIVE = "active"
    TAKE_PROFIT_HIT = "take_profit_hit"
    STOP_LOSS_HIT = "stop_loss_hit"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        return self.value

    @property
    def is_open(self) -> bool:
        """True while the signal is still awaiting or undergoing execution."""
        return self in (SignalStatus.PENDING, SignalStatus.ACTIVE)


@dataclass(slots=True)
class Signal:
    """A generated trading signal: direction, entry/exit plan, and the
    confidence/risk assessment and reasoning behind it."""

    symbol: Symbol
    timeframe: Timeframe
    direction: TradeDecision
    entry_zone: EntryZone
    stop_loss: StopLossLevel
    take_profits: list[TakeProfitLevel]
    confidence: ConfidenceScore
    risk_score: RiskScore
    risk_reward_ratio: RiskRewardRatio
    reasoning: str
    created_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: SignalStatus = SignalStatus.PENDING
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.direction.is_actionable:
            raise InvalidSignalError("A Signal cannot be created with direction NO_TRADE.")
        if not self.take_profits:
            raise InvalidSignalError("A Signal must have at least one take-profit level.")
        total_fraction = sum(tp.size_fraction for tp in self.take_profits)
        if abs(total_fraction - 1.0) > 1e-6:
            raise InvalidSignalError(
                f"Take-profit size fractions must sum to 1.0, got {total_fraction}."
            )

    @property
    def strength(self) -> SignalStrength:
        """The human-readable strength classification derived from confidence."""
        return SignalStrength.from_confidence(self.confidence)

    def activate(self) -> None:
        """Transition the signal from PENDING to ACTIVE once entry has been filled."""
        if self.status is not SignalStatus.PENDING:
            raise InvalidSignalError(
                f"Cannot activate signal '{self.id}' from status '{self.status}'."
            )
        self.status = SignalStatus.ACTIVE

    def close(self, status: SignalStatus) -> None:
        """Transition an open signal to a terminal status."""
        if not self.status.is_open:
            raise InvalidSignalError(
                f"Cannot close signal '{self.id}' already in terminal status '{self.status}'."
            )
        if status.is_open:
            raise InvalidSignalError(f"'{status}' is not a terminal signal status.")
        self.status = status
