"""
SQLAlchemy ORM model: candle.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.candle import Candle
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.infrastructure.database.base import Base


class CandleModel(Base):
    """Persistence model for `Candle`.

    `Candle` has no natural identity of its own in the domain layer; the
    (symbol, timeframe, timestamp) triple is unique, so it backs a surrogate
    integer primary key plus a matching unique constraint.
    """

    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", "timestamp", name="uq_candles_symbol_tf_ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    def to_entity(self) -> Candle:
        """Map this row to the `Candle` domain entity."""
        return Candle(
            symbol=Symbol(self.symbol),
            timeframe=Timeframe.from_string(self.timeframe),
            timestamp=self.timestamp,
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
        )

    @classmethod
    def from_entity(cls, entity: Candle) -> "CandleModel":
        """Build a new row from a `Candle` domain entity."""
        return cls(
            symbol=entity.symbol.value,
            timeframe=entity.timeframe.value,
            timestamp=entity.timestamp,
            open=entity.open,
            high=entity.high,
            low=entity.low,
            close=entity.close,
            volume=entity.volume,
        )
