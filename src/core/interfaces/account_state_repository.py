"""
ABC for account state persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.domain.entities.account_state import AccountState


class AccountStateRepository(ABC):
    """Contract for persisting and retrieving the account's current risk
    state, consulted by risk-management services before approving new
    signals and updated after every position change."""

    @abstractmethod
    async def get_current(self) -> AccountState:
        """Return the current account state.

        Raises:
            EntityNotFoundError: if no account state has been initialized yet.
        """
        raise NotImplementedError

    @abstractmethod
    async def save(self, state: AccountState) -> AccountState:
        """Persist `state` as the new current account state, returning the
        saved instance."""
        raise NotImplementedError
