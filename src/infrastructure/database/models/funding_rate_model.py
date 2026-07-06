"""
SQLAlchemy ORM model: funding_rate.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.funding_rate import FundingRate
from src.core.domain.value_objects.symbol import Symbol
from src.infrastructure.database.base import Base


class FundingRateModel(Base):
    """Persistence model for `FundingRate`."""

    __tablename__ = "funding_rates"
    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_funding_rates_symbol_ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    next_funding_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_entity(self) -> FundingRate:
        """Map this row to the `FundingRate` domain entity."""
        return FundingRate(
            symbol=Symbol(self.symbol),
            rate=self.rate,
            timestamp=self.timestamp,
            next_funding_time=self.next_funding_time,
        )

    @classmethod
    def from_entity(cls, entity: FundingRate) -> "FundingRateModel":
        """Build a new row from a `FundingRate` domain entity."""
        return cls(
            symbol=entity.symbol.value,
            rate=entity.rate,
            timestamp=entity.timestamp,
            next_funding_time=entity.next_funding_time,
        )
