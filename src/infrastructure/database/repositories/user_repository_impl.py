"""
Repository implementation: user.
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select

from src.core.domain.entities.user import User
from src.core.interfaces.user_repository import UserRepository
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyUserRepository(BaseRepository[UserModel], UserRepository):
    """`UserRepository` implementation backed by PostgreSQL via SQLAlchemy."""

    model_type = UserModel

    async def save(self, user: User) -> User:
        model = UserModel.from_entity(user)
        self._session.add(model)
        await self._flush()
        return model.to_entity()

    async def update(self, user: User) -> User:
        model = await self._get_model_by_id(user.id)
        model.apply_entity(user)
        await self._flush()
        return model.to_entity()

    async def get_by_id(self, user_id: str) -> User:
        model = await self._get_model_by_id(user_id)
        return model.to_entity()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return model.to_entity() if model is not None else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return model.to_entity() if model is not None else None

    async def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
        stmt = select(UserModel).order_by(UserModel.created_at.asc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]
