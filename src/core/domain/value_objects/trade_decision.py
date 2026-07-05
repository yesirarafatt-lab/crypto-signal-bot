"""
TradeDecision enum: BUY, SELL, NO_TRADE.
"""

from __future__ import annotations

from enum import Enum


class TradeDecision(str, Enum):
    """The directional outcome of a signal-generation or strategy evaluation."""

    BUY = "buy"
    SELL = "sell"
    NO_TRADE = "no_trade"

    def __str__(self) -> str:
        return self.value

    @property
    def is_actionable(self) -> bool:
        """True for BUY/SELL, False for NO_TRADE."""
        return self is not TradeDecision.NO_TRADE

    def opposite(self) -> "TradeDecision":
        """Return the opposing directional decision. NO_TRADE has no opposite."""
        if self is TradeDecision.BUY:
            return TradeDecision.SELL
        if self is TradeDecision.SELL:
            return TradeDecision.BUY
        raise ValueError("NO_TRADE has no opposite trade decision.")
