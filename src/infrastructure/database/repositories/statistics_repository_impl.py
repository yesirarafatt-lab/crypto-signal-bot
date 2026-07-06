"""
Repository implementation: statistics.
"""

from __future__ import annotations

from datetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.infrastructure.database.models.daily_statistics_model import DailyStatisticsModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository

_UPSERT_COLUMNS = (
    "total_signals",
    "wins",
    "losses",
    "win_rate",
    "total_pnl",
    "total_pnl_percent",
    "avg_r_multiple",
    "best_trade_pnl",
    "worst_trade_pnl",
)


class SqlAlchemyStatisticsRepository(BaseRepository[DailyStatisticsModel]):
    """Persistence for precomputed `DailyStatisticsModel` rollups. No
    `core.interfaces` port is defined for this derived, infrastructure-only
    reporting concern; consumed directly by the dashboard API and the
    scheduled statistics-aggregation job."""

    model_type = DailyStatisticsModel

    async def upsert_daily(self, stats: dict) -> None:
        """Insert or replace the rollup row for `stats["trade_date"]`."""
        stmt = pg_insert(DailyStatisticsModel).values(**stats)
        stmt = stmt.on_conflict_do_update(
            index_elements=[DailyStatisticsModel.trade_date],
            set_={column: getattr(stmt.excluded, column) for column in _UPSERT_COLUMNS},
        )
        await self._session.execute(stmt)
        await self._flush()

    async def get_by_date(self, trade_date: date) -> DailyStatisticsModel | None:
        return await self._session.get(DailyStatisticsModel, trade_date)

    async def get_range(self, start: date, end: date) -> Sequence[DailyStatisticsModel]:
        stmt = (
            select(DailyStatisticsModel)
            .where(
                DailyStatisticsModel.trade_date >= start, DailyStatisticsModel.trade_date <= end
            )
            .order_by(DailyStatisticsModel.trade_date.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
