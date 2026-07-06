"""
Repository implementation: account_state.
"""

from __future__ import annotations

from sqlalchemy import select

from src.core.domain.entities.account_state import AccountState
from src.core.exceptions.repository_exceptions import EntityNotFoundError
from src.core.interfaces.account_state_repository import AccountStateRepository
from src.infrastructure.database.models.account_state_model import AccountStateModel
from src.infrastructure.database.repositories.base_repository_impl import BaseRepository


class SqlAlchemyAccountStateRepository(BaseRepository[AccountStateModel], AccountStateRepository):
    """`AccountStateRepository` implementation backed by PostgreSQL via SQLAlchemy.

    The "current" state is the most recently updated row; every `save` call
    inserts a new snapshot rather than overwriting history, so this table
    also doubles as an audit trail of the account's risk state over time.
    """

    model_type = AccountStateModel

    async def get_current(self) -> AccountState:
        stmt = select(AccountStateModel).order_by(AccountStateModel.updated_at.desc()).limit(1)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model is None:
            raise EntityNotFoundError("No account state has been initialized yet.")
        return model.to_entity()

    async def save(self, state: AccountState) -> AccountState:
        model = AccountStateModel.from_entity(state)
        self._session.add(model)
        await self._flush()
        return model.to_entity()
