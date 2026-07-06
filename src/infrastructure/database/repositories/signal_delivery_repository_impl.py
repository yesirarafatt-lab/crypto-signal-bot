"""
Repository implementation: signal_delivery.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select

from src.infrastructure.database.models.signal_delivery_model import SignalDeliveryModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemySignalDeliveryRepository(BaseRepository[SignalDeliveryModel]):
    """Persistence for signal-delivery attempts. No `core.interfaces` port is
    defined for this infrastructure-only concern; consumed directly by the
    notification fan-out job to avoid duplicate sends and report delivery
    success rates."""

    model_type = SignalDeliveryModel

    async def record(
        self,
        signal_id: str,
        user_id: str,
        channel: str,
        success: bool,
        delivered_at: datetime,
        error_message: str | None = None,
    ) -> SignalDeliveryModel:
        model = SignalDeliveryModel(
            signal_id=signal_id,
            user_id=user_id,
            channel=channel,
            success=success,
            delivered_at=delivered_at,
            error_message=error_message,
        )
        self._session.add(model)
        await self._flush()
        return model

    async def was_delivered(self, signal_id: str, user_id: str, channel: str) -> bool:
        """True if a successful delivery to `user_id` over `channel` for
        `signal_id` has already been recorded, guarding against duplicate sends."""
        stmt = select(SignalDeliveryModel).where(
            SignalDeliveryModel.signal_id == signal_id,
            SignalDeliveryModel.user_id == user_id,
            SignalDeliveryModel.channel == channel,
            SignalDeliveryModel.success.is_(True),
        )
        result = await self._session.execute(stmt)
        return result.scalars().first() is not None

    async def get_for_signal(self, signal_id: str) -> Sequence[SignalDeliveryModel]:
        stmt = select(SignalDeliveryModel).where(SignalDeliveryModel.signal_id == signal_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
