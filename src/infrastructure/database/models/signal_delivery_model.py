"""
SQLAlchemy ORM model: signal_delivery.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class SignalDeliveryModel(Base):
    """A record of a signal notification delivery attempt to a specific user
    over a specific channel, used to avoid duplicate sends and to power
    delivery-success reporting. No corresponding core domain entity; this is
    an infrastructure-only cross-cutting concern of the notification layer.
    """

    __tablename__ = "signal_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "signal_id", "user_id", "channel", name="uq_signal_deliveries_signal_user_channel"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    signal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
