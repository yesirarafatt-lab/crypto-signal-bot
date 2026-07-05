"""
ABC for caching layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CacheProvider(ABC):
    """Contract for a key-value cache used to reduce redundant exchange calls
    and share short-lived state across scheduler jobs and API workers."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return the cached value for `key`, or None if absent or expired."""
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Store `value` under `key`, expiring after `ttl_seconds` if given."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove `key` from the cache. Must not raise if `key` is absent."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """True if `key` is present in the cache and not expired."""
        raise NotImplementedError

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomically increment the integer counter at `key` by `amount`.

        Creates the counter starting at `amount` if `key` does not yet exist.
        Returns the counter's new value.
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Release any underlying connections held by this cache provider."""
        raise NotImplementedError
