"""
ABC for user persistence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from src.core.domain.entities.user import User


class UserRepository(ABC):
    """Contract for persisting and querying user identities."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persist a new user, returning the saved instance.

        Raises:
            DuplicateEntityError: if a user with the same telegram_id or
                email already exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        """Persist changes to an existing user.

        Raises:
            EntityNotFoundError: if no user with this id exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User:
        """Return the user with `user_id`.

        Raises:
            EntityNotFoundError: if no such user exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Return the user with `telegram_id`, or None if none exists."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Return the user with `email`, or None if none exists."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
        """Return users ordered by creation date, paginated by `limit`/`offset`."""
        raise NotImplementedError
