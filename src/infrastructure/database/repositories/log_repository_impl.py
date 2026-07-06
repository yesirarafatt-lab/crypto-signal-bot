"""
Repository implementation: log.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping, Sequence

from sqlalchemy import select

from src.infrastructure.database.models.log_entry_model import LogEntryModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyLogRepository(BaseRepository[LogEntryModel]):
    """Persistence for structured application log entries. No `core.interfaces`
    port is defined for this infrastructure-only concern; consumed directly
    by a logging handler that wants a durable, queryable log sink in
    addition to stdout/file logging."""

    model_type = LogEntryModel

    async def save(
        self,
        level: str,
        logger_name: str,
        message: str,
        context: Mapping[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> None:
        model = LogEntryModel(
            level=level,
            logger_name=logger_name,
            message=message,
            context=dict(context) if context else {},
            created_at=created_at or datetime.utcnow(),
        )
        self._session.add(model)
        await self._flush()

    async def get_recent(
        self, level: str | None = None, limit: int = 100
    ) -> Sequence[LogEntryModel]:
        stmt = select(LogEntryModel)
        if level is not None:
            stmt = stmt.where(LogEntryModel.level == level)
        stmt = stmt.order_by(LogEntryModel.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_older_than(self, cutoff: datetime) -> int:
        stmt = select(LogEntryModel).where(LogEntryModel.created_at < cutoff)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        count = len(models)
        for model in models:
            await self._session.delete(model)
        await self._flush()
        return count
