"""
SQLAlchemy ORM model: liquidation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.liquidation_event import LiquidationEvent
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.infrastructure.database.base import Base


class LiquidationModel(Base):
    """Persistence model for `LiquidationEvent`."""

    __tablename__ = "liquidations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    def to_entity(self) -> LiquidationEvent:
        """Map this row to the `LiquidationEvent` domain entity."""
        return LiquidationEvent(
            symbol=Symbol(self.symbol),
            side=TradeDecision(self.side),
            price=self.price,
            quantity=self.quantity,
            timestamp=self.timestamp,
            id=self.id,
        )

    @classmethod
    def from_entity(cls, entity: LiquidationEvent) -> "LiquidationModel":
        """Build a new row from a `LiquidationEvent` domain entity."""
        return cls(
            id=entity.id,
            symbol=entity.symbol.value,
            side=entity.side.value,
            price=entity.price,
            quantity=entity.quantity,
            timestamp=entity.timestamp,
        )
