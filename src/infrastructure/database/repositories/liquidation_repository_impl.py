"""
Repository implementation: liquidation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select

from src.core.domain.entities.liquidation_event import LiquidationEvent
from src.core.domain.value_objects.symbol import Symbol
from src.infrastructure.database.models.liquidation_model import LiquidationModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyLiquidationRepository(BaseRepository[LiquidationModel]):
    """Persistence for `LiquidationEvent` records, feeding liquidation-cluster
    and cascade detection. No `core.interfaces` port is defined for this
    entity; consumed directly by the application services that need it."""

    model_type = LiquidationModel

    async def save(self, event: LiquidationEvent) -> None:
        model = LiquidationModel.from_entity(event)
        self._session.add(model)
        await self._flush()

    async def save_many(self, events: Sequence[LiquidationEvent]) -> None:
        for event in events:
            self._session.add(LiquidationModel.from_entity(event))
        await self._flush()

    async def get_recent(
        self, symbol: Symbol, since: datetime, limit: int = 500
    ) -> Sequence[LiquidationEvent]:
        stmt = (
            select(LiquidationModel)
            .where(LiquidationModel.symbol == symbol.value, LiquidationModel.timestamp >= since)
            .order_by(LiquidationModel.timestamp.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        models.reverse()
        return [model.to_entity() for model in models]

    async def delete_older_than(self, cutoff: datetime) -> int:
        stmt = select(LiquidationModel).where(LiquidationModel.timestamp < cutoff)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        count = len(models)
        for model in models:
            await self._session.delete(model)
        await self._flush()
        return count
