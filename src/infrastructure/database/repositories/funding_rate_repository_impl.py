"""
Repository implementation: funding_rate.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.core.domain.entities.funding_rate import FundingRate
from src.core.domain.value_objects.symbol import Symbol
from src.infrastructure.database.models.funding_rate_model import FundingRateModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyFundingRateRepository(BaseRepository[FundingRateModel]):
    """Persistence for `FundingRate` snapshots.

    No `core.interfaces` port is defined for funding rates, unlike candles;
    it is consumed directly by the application services that need it, kept
    behind this repository purely to isolate SQLAlchemy from callers.
    """

    model_type = FundingRateModel

    async def save(self, funding_rate: FundingRate) -> None:
        stmt = pg_insert(FundingRateModel).values(
            symbol=funding_rate.symbol.value,
            rate=funding_rate.rate,
            timestamp=funding_rate.timestamp,
            next_funding_time=funding_rate.next_funding_time,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_funding_rates_symbol_ts",
            set_={
                "rate": stmt.excluded.rate,
                "next_funding_time": stmt.excluded.next_funding_time,
            },
        )
        await self._session.execute(stmt)
        await self._flush()

    async def get_latest(self, symbol: Symbol, limit: int = 100) -> Sequence[FundingRate]:
        stmt = (
            select(FundingRateModel)
            .where(FundingRateModel.symbol == symbol.value)
            .order_by(FundingRateModel.timestamp.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        models.reverse()
        return [model.to_entity() for model in models]

    async def get_range(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> Sequence[FundingRate]:
        stmt = (
            select(FundingRateModel)
            .where(
                FundingRateModel.symbol == symbol.value,
                FundingRateModel.timestamp >= start,
                FundingRateModel.timestamp <= end,
            )
            .order_by(FundingRateModel.timestamp.asc())
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]
