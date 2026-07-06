"""
Repository implementation: api_key.
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select

from src.infrastructure.database.models.api_key_model import ApiKeyModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyApiKeyRepository(BaseRepository[ApiKeyModel]):
    """Persistence for encrypted exchange API credentials. No `core.interfaces`
    port is defined for this infrastructure-only concern; consumed directly
    by the exchange-client wiring that needs per-user credentials."""

    model_type = ApiKeyModel

    async def save(self, api_key: ApiKeyModel) -> ApiKeyModel:
        self._session.add(api_key)
        await self._flush()
        return api_key

    async def get_by_id(self, api_key_id: str) -> ApiKeyModel:
        return await self._get_model_by_id(api_key_id)

    async def get_active_for_user(self, user_id: str) -> Sequence[ApiKeyModel]:
        stmt = select(ApiKeyModel).where(
            ApiKeyModel.user_id == user_id, ApiKeyModel.is_active.is_(True)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_exchange(
        self, user_id: str, exchange_name: str
    ) -> ApiKeyModel | None:
        stmt = select(ApiKeyModel).where(
            ApiKeyModel.user_id == user_id,
            ApiKeyModel.exchange_name == exchange_name,
            ApiKeyModel.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def deactivate(self, api_key_id: str) -> None:
        model = await self._get_model_by_id(api_key_id)
        model.is_active = False
        await self._flush()
