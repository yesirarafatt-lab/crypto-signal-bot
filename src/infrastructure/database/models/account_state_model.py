"""
SQLAlchemy ORM model: account_state.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.account_state import AccountState
from src.infrastructure.database.base import Base


class AccountStateModel(Base):
    """Persistence model for `AccountState`.

    Only one row is treated as "current" at a time by the repository
    (the most recently updated one); history is retained for auditing.
    """

    __tablename__ = "account_states"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    equity: Mapped[float] = mapped_column(Float, nullable=False)
    available_balance: Mapped[float] = mapped_column(Float, nullable=False)
    daily_pnl: Mapped[float] = mapped_column(Float, nullable=False)
    open_positions_count: Mapped[int] = mapped_column(Integer, nullable=False)
    consecutive_losses: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def to_entity(self) -> AccountState:
        """Map this row to the `AccountState` domain entity."""
        return AccountState(
            equity=self.equity,
            available_balance=self.available_balance,
            daily_pnl=self.daily_pnl,
            open_positions_count=self.open_positions_count,
            consecutive_losses=self.consecutive_losses,
            updated_at=self.updated_at,
            id=self.id,
            cooldown_until=self.cooldown_until,
        )

    @classmethod
    def from_entity(cls, entity: AccountState) -> "AccountStateModel":
        """Build a new row from an `AccountState` domain entity."""
        return cls(
            id=entity.id,
            equity=entity.equity,
            available_balance=entity.available_balance,
            daily_pnl=entity.daily_pnl,
            open_positions_count=entity.open_positions_count,
            consecutive_losses=entity.consecutive_losses,
            updated_at=entity.updated_at,
            cooldown_until=entity.cooldown_until,
        )
