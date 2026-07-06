"""
SQLAlchemy ORM model: subscription.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.subscription import Subscription
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.infrastructure.database.base import Base


class SubscriptionModel(Base):
    """Persistence model for `Subscription`."""

    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "symbol", "timeframe", name="uq_subscriptions_user_symbol_tf"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(5), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def to_entity(self) -> Subscription:
        """Map this row to the `Subscription` domain entity."""
        return Subscription(
            user_id=self.user_id,
            symbol=Symbol(self.symbol),
            timeframe=Timeframe.from_string(self.timeframe),
            created_at=self.created_at,
            id=self.id,
            is_active=self.is_active,
        )

    @classmethod
    def from_entity(cls, entity: Subscription) -> "SubscriptionModel":
        """Build a new row from a `Subscription` domain entity."""
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            symbol=entity.symbol.value,
            timeframe=entity.timeframe.value,
            created_at=entity.created_at,
            is_active=entity.is_active,
        )

    def apply_entity(self, entity: Subscription) -> None:
        """Update this row's mutable `is_active` flag in place from `entity`."""
        self.is_active = entity.is_active
