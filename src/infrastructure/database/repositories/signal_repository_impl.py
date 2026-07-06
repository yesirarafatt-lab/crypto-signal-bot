"""
Repository implementation: signal.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select

from src.core.domain.entities.signal import Signal, SignalStatus
from src.core.domain.value_objects.symbol import Symbol
from src.core.interfaces.signal_repository import SignalRepository
from src.infrastructure.database.models.signal_model import SignalModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemySignalRepository(BaseRepository[SignalModel], SignalRepository):
    """`SignalRepository` implementation backed by PostgreSQL via SQLAlchemy."""

    model_type = SignalModel

    async def save(self, signal: Signal) -> Signal:
        model = SignalModel.from_entity(signal)
        self._session.add(model)
        await self._flush()
        return model.to_entity()

    async def update(self, signal: Signal) -> Signal:
        model = await self._get_model_by_id(signal.id)
        model.apply_entity(signal)
        await self._flush()
        return model.to_entity()

    async def get_by_id(self, signal_id: str) -> Signal:
        model = await self._get_model_by_id(signal_id)
        return model.to_entity()

    async def get_open_signals(self, symbol: Symbol | None = None) -> Sequence[Signal]:
        open_statuses = [SignalStatus.PENDING.value, SignalStatus.ACTIVE.value]
        stmt = select(SignalModel).where(SignalModel.status.in_(open_statuses))
        if symbol is not None:
            stmt = stmt.where(SignalModel.symbol == symbol.value)
        stmt = stmt.order_by(SignalModel.created_at.desc())
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def get_history(
        self,
        symbol: Symbol | None = None,
        status: SignalStatus | None = None,
        since: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Signal]:
        stmt = select(SignalModel)
        if symbol is not None:
            stmt = stmt.where(SignalModel.symbol == symbol.value)
        if status is not None:
            stmt = stmt.where(SignalModel.status == status.value)
        if since is not None:
            stmt = stmt.where(SignalModel.created_at >= since)
        stmt = stmt.order_by(SignalModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]
