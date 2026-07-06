"""
Repository implementation: subscription.
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import select

from src.core.domain.entities.subscription import Subscription
from src.core.domain.value_objects.symbol import Symbol
from src.core.domain.value_objects.timeframe import Timeframe
from src.infrastructure.database.models.subscription_model import SubscriptionModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemySubscriptionRepository(BaseRepository[SubscriptionModel]):
    """Persistence for `Subscription` records. No `core.interfaces` port is
    defined for this entity; consumed directly by the application services
    that need it (subscription management use cases, the notification
    fan-out job)."""

    model_type = SubscriptionModel

    async def save(self, subscription: Subscription) -> Subscription:
        model = SubscriptionModel.from_entity(subscription)
        self._session.add(model)
        await self._flush()
        return model.to_entity()

    async def update(self, subscription: Subscription) -> Subscription:
        model = await self._get_model_by_id(subscription.id)
        model.apply_entity(subscription)
        await self._flush()
        return model.to_entity()

    async def get_by_id(self, subscription_id: str) -> Subscription:
        model = await self._get_model_by_id(subscription_id)
        return model.to_entity()

    async def get_by_user(self, user_id: str) -> Sequence[Subscription]:
        stmt = select(SubscriptionModel).where(SubscriptionModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def get_active_subscribers(
        self, symbol: Symbol, timeframe: Timeframe
    ) -> Sequence[Subscription]:
        stmt = select(SubscriptionModel).where(
            SubscriptionModel.symbol == symbol.value,
            SubscriptionModel.timeframe == timeframe.value,
            SubscriptionModel.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]
