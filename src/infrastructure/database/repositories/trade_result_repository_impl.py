"""
Repository implementation: trade_result.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select

from src.core.domain.entities.trade_result import TradeResult
from src.core.domain.value_objects.symbol import Symbol
from src.infrastructure.database.models.trade_result_model import TradeResultModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyTradeResultRepository(BaseRepository[TradeResultModel]):
    """Persistence for `TradeResult` records. No `core.interfaces` port is
    defined for this entity; consumed directly by the statistics/reporting
    services that need it."""

    model_type = TradeResultModel

    async def save(self, trade_result: TradeResult) -> TradeResult:
        model = TradeResultModel.from_entity(trade_result)
        self._session.add(model)
        await self._flush()
        return model.to_entity()

    async def get_by_id(self, trade_result_id: str) -> TradeResult:
        model = await self._get_model_by_id(trade_result_id)
        return model.to_entity()

    async def get_history(
        self,
        symbol: Symbol | None = None,
        since: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[TradeResult]:
        stmt = select(TradeResultModel)
        if symbol is not None:
            stmt = stmt.where(TradeResultModel.symbol == symbol.value)
        if since is not None:
            stmt = stmt.where(TradeResultModel.closed_at >= since)
        stmt = stmt.order_by(TradeResultModel.closed_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def get_closed_between(self, start: datetime, end: datetime) -> Sequence[TradeResult]:
        """Return every trade result closed within [start, end], used by the
        daily-statistics aggregation job."""
        stmt = select(TradeResultModel).where(
            TradeResultModel.closed_at >= start, TradeResultModel.closed_at <= end
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]
