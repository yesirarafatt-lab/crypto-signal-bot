"""
Repository implementation: open_interest.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.core.domain.entities.open_interest import OpenInterest
from src.core.domain.value_objects.symbol import Symbol
from src.infrastructure.database.models.open_interest_model import OpenInterestModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyOpenInterestRepository(BaseRepository[OpenInterestModel]):
    """Persistence for `OpenInterest` snapshots.

    No `core.interfaces` port is defined for open interest; it is consumed
    directly by the application services that need it, kept behind this
    repository purely to isolate SQLAlchemy from callers.
    """

    model_type = OpenInterestModel

    async def save(self, open_interest: OpenInterest) -> None:
        stmt = pg_insert(OpenInterestModel).values(
            symbol=open_interest.symbol.value,
            value=open_interest.value,
            timestamp=open_interest.timestamp,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_open_interests_symbol_ts",
            set_={"value": stmt.excluded.value},
        )
        await self._session.execute(stmt)
        await self._flush()

    async def get_latest(self, symbol: Symbol, limit: int = 100) -> Sequence[OpenInterest]:
        stmt = (
            select(OpenInterestModel)
            .where(OpenInterestModel.symbol == symbol.value)
            .order_by(OpenInterestModel.timestamp.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        models.reverse()
        return [model.to_entity() for model in models]

    async def get_range(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> Sequence[OpenInterest]:
        stmt = (
            select(OpenInterestModel)
            .where(
                OpenInterestModel.symbol == symbol.value,
                OpenInterestModel.timestamp >= start,
                OpenInterestModel.timestamp <= end,
            )
            .order_by(OpenInterestModel.timestamp.asc())
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]
