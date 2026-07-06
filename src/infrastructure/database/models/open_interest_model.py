"""
SQLAlchemy ORM model: open_interest.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.open_interest import OpenInterest
from src.core.domain.value_objects.symbol import Symbol
from src.infrastructure.database.base import Base


class OpenInterestModel(Base):
    """Persistence model for `OpenInterest`."""

    __tablename__ = "open_interests"
    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_open_interests_symbol_ts"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    def to_entity(self) -> OpenInterest:
        """Map this row to the `OpenInterest` domain entity."""
        return OpenInterest(symbol=Symbol(self.symbol), value=self.value, timestamp=self.timestamp)

    @classmethod
    def from_entity(cls, entity: OpenInterest) -> "OpenInterestModel":
        """Build a new row from an `OpenInterest` domain entity."""
        return cls(symbol=entity.symbol.value, value=entity.value, timestamp=entity.timestamp)
