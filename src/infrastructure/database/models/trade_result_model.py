"""
SQLAlchemy ORM model: trade_result.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Float, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.trade_result import ExitReason, TradeResult
from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.infrastructure.database.base import Base

_PRICE_NUMERIC = Numeric(24, 10)


class TradeResultModel(Base):
    """Persistence model for `TradeResult`."""

    __tablename__ = "trade_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    signal_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    position_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    exit_price: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    price_precision: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    pnl: Mapped[float] = mapped_column(Float, nullable=False)
    pnl_percent: Mapped[float] = mapped_column(Float, nullable=False)
    r_multiple: Mapped[float] = mapped_column(Float, nullable=False)
    exit_reason: Mapped[str] = mapped_column(String(20), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    def to_entity(self) -> TradeResult:
        """Map this row to the `TradeResult` domain entity."""
        precision = int(self.price_precision)
        return TradeResult(
            signal_id=self.signal_id,
            position_id=self.position_id,
            symbol=Symbol(self.symbol),
            direction=TradeDecision(self.direction),
            entry_price=Price(self.entry_price, precision=precision),
            exit_price=Price(self.exit_price, precision=precision),
            quantity=self.quantity,
            pnl=self.pnl,
            pnl_percent=self.pnl_percent,
            r_multiple=self.r_multiple,
            exit_reason=ExitReason(self.exit_reason),
            opened_at=self.opened_at,
            closed_at=self.closed_at,
            id=self.id,
        )

    @classmethod
    def from_entity(cls, entity: TradeResult) -> "TradeResultModel":
        """Build a new row from a `TradeResult` domain entity."""
        return cls(
            id=entity.id,
            signal_id=entity.signal_id,
            position_id=entity.position_id,
            symbol=entity.symbol.value,
            direction=entity.direction.value,
            entry_price=entity.entry_price.amount,
            exit_price=entity.exit_price.amount,
            price_precision=entity.entry_price.precision,
            quantity=entity.quantity,
            pnl=entity.pnl,
            pnl_percent=entity.pnl_percent,
            r_multiple=entity.r_multiple,
            exit_reason=entity.exit_reason.value,
            opened_at=entity.opened_at,
            closed_at=entity.closed_at,
        )
