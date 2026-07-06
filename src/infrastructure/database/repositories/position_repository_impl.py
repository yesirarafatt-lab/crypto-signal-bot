"""
Repository implementation: position.
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select

from src.core.domain.entities.position import Position, PositionStatus
from src.core.interfaces.position_repository import PositionRepository
from src.infrastructure.database.models.position_model import PositionModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyPositionRepository(BaseRepository[PositionModel], PositionRepository):
    """`PositionRepository` implementation backed by PostgreSQL via SQLAlchemy."""

    model_type = PositionModel

    async def save(self, position: Position) -> Position:
        model = PositionModel.from_entity(position)
        self._session.add(model)
        await self._flush()
        return model.to_entity()

    async def update(self, position: Position) -> Position:
        model = await self._get_model_by_id(position.id)
        model.apply_entity(position)
        await self._flush()
        return model.to_entity()

    async def get_by_id(self, position_id: str) -> Position:
        model = await self._get_model_by_id(position_id)
        return model.to_entity()

    async def get_open_positions(self) -> Sequence[Position]:
        stmt = (
            select(PositionModel)
            .where(PositionModel.status == PositionStatus.OPEN.value)
            .order_by(PositionModel.opened_at.asc())
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def get_by_signal_id(self, signal_id: str) -> Position | None:
        stmt = select(PositionModel).where(PositionModel.signal_id == signal_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return model.to_entity() if model is not None else None
