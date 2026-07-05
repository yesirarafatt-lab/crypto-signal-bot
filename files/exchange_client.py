"""
ABC for exchange market data / trading operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Mapping


class ExchangeClient(ABC):
    """Contract for connecting to, and performing account operations on, an exchange."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish the underlying exchange connection. Must be idempotent."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Release the underlying exchange connection and any held resources."""
        raise NotImplementedError

    @abstractmethod
    async def test_connection(self) -> bool:
        """Verify connectivity and credentials against the exchange. Returns True on success."""
        raise NotImplementedError

    @abstractmethod
    async def load_markets(self, reload: bool = False) -> Mapping[str, Any]:
        """Load (and optionally reload) the exchange's tradable market metadata."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_balance(self) -> Mapping[str, Any]:
        """Fetch the authenticated account's current balance."""
        raise NotImplementedError

    async def __aenter__(self) -> "ExchangeClient":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()
