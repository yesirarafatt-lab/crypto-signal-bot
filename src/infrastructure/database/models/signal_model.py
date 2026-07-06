"""
SQLAlchemy ORM model: signal.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.domain.entities.signal import Signal, SignalStatus
from src.core.domain.value_objects.confidence_score import ConfidenceScore
from src.core.domain.value_objects.entry_zone import EntryZone
from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.risk_reward_ratio import RiskRewardRatio
from src.core.domain.value_objects.risk_score import RiskScore
from src.core.domain.value_objects.stop_loss_level import StopLossBasis, StopLossLevel
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.take_profit_level import TakeProfitLevel
from src.core.domain.value_objects.timeframe import Timeframe
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.core.domain.value_objects.zone_range import ZoneRange
from src.infrastructure.database.base import Base

_PRICE_NUMERIC = Numeric(24, 10)


class SignalTakeProfitModel(Base):
    """A single take-profit target belonging to a `SignalModel`."""

    __tablename__ = "signal_take_profits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    signal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    size_fraction: Mapped[float] = mapped_column(Float, nullable=False)
    label: Mapped[str] = mapped_column(String(20), nullable=False, default="TP1")

    signal: Mapped["SignalModel"] = relationship(back_populates="take_profit_levels")


class SignalModel(Base):
    """Persistence model for `Signal`.

    All prices on a signal (entry zone, stop-loss, take-profits) share a
    single `price_precision`, matching the `Price` default used throughout
    signal generation.
    """

    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(5), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    entry_zone_top: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    entry_zone_bottom: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    entry_zone_preferred: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    stop_loss_price: Mapped[Decimal] = mapped_column(_PRICE_NUMERIC, nullable=False)
    stop_loss_basis: Mapped[str] = mapped_column(String(20), nullable=False)
    price_precision: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score_value: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score_factors: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    risk_reward_ratio: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SignalStatus.PENDING.value, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    take_profit_levels: Mapped[list[SignalTakeProfitModel]] = relationship(
        back_populates="signal",
        order_by="SignalTakeProfitModel.order_index",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_entity(self) -> Signal:
        """Map this row (and its take-profit children) to the `Signal` domain entity."""
        precision = self.price_precision
        entry_zone = EntryZone(
            range=ZoneRange(
                top=Price(self.entry_zone_top, precision=precision),
                bottom=Price(self.entry_zone_bottom, precision=precision),
            ),
            preferred_entry=Price(self.entry_zone_preferred, precision=precision),
        )
        stop_loss = StopLossLevel(
            price=Price(self.stop_loss_price, precision=precision),
            basis=StopLossBasis(self.stop_loss_basis),
        )
        take_profits = [
            TakeProfitLevel(
                price=Price(tp.price, precision=precision),
                size_fraction=tp.size_fraction,
                label=tp.label,
            )
            for tp in sorted(self.take_profit_levels, key=lambda t: t.order_index)
        ]
        return Signal(
            symbol=Symbol(self.symbol),
            timeframe=Timeframe.from_string(self.timeframe),
            direction=TradeDecision(self.direction),
            entry_zone=entry_zone,
            stop_loss=stop_loss,
            take_profits=take_profits,
            confidence=ConfidenceScore(self.confidence_score),
            risk_score=RiskScore(self.risk_score_value, MappingProxyType(self.risk_score_factors)),
            risk_reward_ratio=RiskRewardRatio(Decimal(str(self.risk_reward_ratio))),
            reasoning=self.reasoning,
            created_at=self.created_at,
            id=self.id,
            status=SignalStatus(self.status),
            expires_at=self.expires_at,
        )

    @classmethod
    def from_entity(cls, entity: Signal) -> "SignalModel":
        """Build a new row (and its take-profit children) from a `Signal` domain entity."""
        precision = entity.entry_zone.preferred_entry.precision
        model = cls(
            id=entity.id,
            symbol=entity.symbol.value,
            timeframe=entity.timeframe.value,
            direction=entity.direction.value,
            entry_zone_top=entity.entry_zone.upper_bound.amount,
            entry_zone_bottom=entity.entry_zone.lower_bound.amount,
            entry_zone_preferred=entity.entry_zone.preferred_entry.amount,
            stop_loss_price=entity.stop_loss.price.amount,
            stop_loss_basis=entity.stop_loss.basis.value,
            price_precision=precision,
            confidence_score=entity.confidence.value,
            risk_score_value=entity.risk_score.value,
            risk_score_factors=dict(entity.risk_score.factors),
            risk_reward_ratio=entity.risk_reward_ratio.value,
            reasoning=entity.reasoning,
            created_at=entity.created_at,
            status=entity.status.value,
            expires_at=entity.expires_at,
        )
        model.take_profit_levels = [
            SignalTakeProfitModel(
                order_index=index,
                price=tp.price.amount,
                size_fraction=tp.size_fraction,
                label=tp.label,
            )
            for index, tp in enumerate(entity.take_profits)
        ]
        return model

    def apply_entity(self, entity: Signal) -> None:
        """Update this row's mutable fields (status/expiry) in place from `entity`.

        The entry/exit plan is treated as immutable once a signal is created;
        only lifecycle fields are expected to change after persistence.
        """
        self.status = entity.status.value
        self.expires_at = entity.expires_at
