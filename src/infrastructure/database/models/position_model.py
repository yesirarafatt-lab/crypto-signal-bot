"""
SQLAlchemy ORM model: position.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.domain.entities.position import Position, PositionStatus
from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.stop_loss_level import StopLossBasis, StopLossLevel
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.take_profit_level import TakeProfitLevel
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.infrastructure.database.base import Base

_PRICE_NUMERIC = Numeric(24, 10)


class PositionTakeProfitModel(Base):
    """A single take-profit target belonging to a `PositionModel`."""

    __tablename__ = "position_take_profits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    position_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("positions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    size_fraction: Mapped[float] = mapped_column(Float, nullable=False)
    label: Mapped[str] = mapped_column(String(20), nullable=False, default="TP1")

    position: Mapped["PositionModel"] = relationship(back_populates="take_profit_levels")


class PositionModel(Base):
    """Persistence model for `Position`.

    All prices on a position (entry, stop-loss, take-profits) share a single
    `price_precision`, matching the `Price` default used at signal generation.
    """

    __tablename__ = "positions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    signal_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss_price: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    stop_loss_basis: Mapped[str] = mapped_column(String(20), nullable=False)
    price_precision: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default=PositionStatus.OPEN.value, index=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    take_profit_levels: Mapped[list[PositionTakeProfitModel]] = relationship(
        back_populates="position",
        order_by="PositionTakeProfitModel.order_index",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_entity(self) -> Position:
        """Map this row (and its take-profit children) to the `Position` domain entity."""
        precision = self.price_precision
        take_profits = [
            TakeProfitLevel(
                price=Price(tp.price, precision=precision),
                size_fraction=tp.size_fraction,
                label=tp.label,
            )
            for tp in sorted(self.take_profit_levels, key=lambda t: t.order_index)
        ]
        return Position(
            signal_id=self.signal_id,
            symbol=Symbol(self.symbol),
            direction=TradeDecision(self.direction),
            entry_price=Price(self.entry_price, precision=precision),
            quantity=self.quantity,
            stop_loss=StopLossLevel(
                price=Price(self.stop_loss_price, precision=precision),
                basis=StopLossBasis(self.stop_loss_basis),
            ),
            take_profits=take_profits,
            opened_at=self.opened_at,
            id=self.id,
            status=PositionStatus(self.status),
            closed_at=self.closed_at,
        )

    @classmethod
    def from_entity(cls, entity: Position) -> "PositionModel":
        """Build a new row (and its take-profit children) from a `Position` domain entity."""
        model = cls(
            id=entity.id,
            signal_id=entity.signal_id,
            symbol=entity.symbol.value,
            direction=entity.direction.value,
            entry_price=entity.entry_price.amount,
            quantity=entity.quantity,
            stop_loss_price=entity.stop_loss.price.amount,
            stop_loss_basis=entity.stop_loss.basis.value,
            price_precision=entity.entry_price.precision,
            opened_at=entity.opened_at,
            status=entity.status.value,
            closed_at=entity.closed_at,
        )
        model.take_profit_levels = [
            PositionTakeProfitModel(
                order_index=index,
                price=tp.price.amount,
                size_fraction=tp.size_fraction,
                label=tp.label,
            )
            for index, tp in enumerate(entity.take_profits)
        ]
        return model

    def apply_entity(self, entity: Position) -> None:
        """Update this row's mutable fields (stop-loss, status, close time) in
        place from `entity`. The entry price, quantity, and take-profit plan
        are treated as immutable once a position is opened."""
        self.stop_loss_price = entity.stop_loss.price.amount
        self.stop_loss_basis = entity.stop_loss.basis.value
        self.status = entity.status.value
        self.closed_at = entity.closed_at
