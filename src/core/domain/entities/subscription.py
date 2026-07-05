"""
User subscription entity (symbol/timeframe watchlist).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe


@dataclass(slots=True)
class Subscription:
    """A user's subscription to signal notifications for a given
    symbol/timeframe pair."""

    user_id: str
    symbol: Symbol
    timeframe: Timeframe
    created_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True

    def deactivate(self) -> None:
        """Stop receiving notifications for this subscription without deleting it."""
        self.is_active = False

    def reactivate(self) -> None:
        """Resume notifications for a previously deactivated subscription."""
        self.is_active = True
