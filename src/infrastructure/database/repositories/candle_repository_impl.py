"""
Repository implementation: candle.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.core.domain.entities.candle import Candle
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.core.interfaces.candle_repository import CandleRepository
from src.infrastructure.database.models.candle_model import CandleModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository

_UPSERT_COLUMNS = ("open", "high", "low", "close", "volume")


class SqlAlchemyCandleRepository(BaseRepository[CandleModel], CandleRepository):
    """`CandleRepository` implementation backed by PostgreSQL via SQLAlchemy.

    Uses a PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` upsert on the
    (symbol, timeframe, timestamp) unique constraint so repeated ingestion
    of the same candle (e.g. an in-progress candle re-fetched every poll) is
    idempotent.
    """

    model_type = CandleModel

    async def save(self, candle: Candle) -> None:
        await self.save_many([candle])

    async def save_many(self, candles: Sequence[Candle]) -> None:
        if not candles:
            return
        rows = [
            {
                "symbol": candle.symbol.value,
                "timeframe": candle.timeframe.value,
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
            }
            for candle in candles
        ]
        stmt = pg_insert(CandleModel).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_candles_symbol_tf_ts",
            set_={column: getattr(stmt.excluded, column) for column in _UPSERT_COLUMNS},
        )
        await self._session.execute(stmt)
        await self._flush()

    async def get_latest(
        self, symbol: Symbol, timeframe: Timeframe, limit: int = 200
    ) -> Sequence[Candle]:
        stmt = (
            select(CandleModel)
            .where(CandleModel.symbol == symbol.value, CandleModel.timeframe == timeframe.value)
            .order_by(CandleModel.timestamp.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        models.reverse()  # oldest to newest, as documented by the interface
        return [model.to_entity() for model in models]

    async def get_range(
        self, symbol: Symbol, timeframe: Timeframe, start: datetime, end: datetime
    ) -> Sequence[Candle]:
        stmt = (
            select(CandleModel)
            .where(
                CandleModel.symbol == symbol.value,
                CandleModel.timeframe == timeframe.value,
                CandleModel.timestamp >= start,
                CandleModel.timestamp <= end,
            )
            .order_by(CandleModel.timestamp.asc())
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def delete_older_than(self, cutoff: datetime) -> int:
        stmt = select(CandleModel).where(CandleModel.timestamp < cutoff)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        count = len(models)
        for model in models:
            await self._session.delete(model)
        await self._flush()
        return count
