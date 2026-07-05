"""
Async token-bucket rate limiter for outbound exchange calls.
"""

from __future__ import annotations

import asyncio
import time
from types import TracebackType


class TokenBucketRateLimiter:
    """Coroutine-safe async token-bucket limiter capping outbound request rate.

    Tokens refill continuously at `requests_per_second`. Each call to
    `acquire()` blocks until enough tokens are available, which smooths
    bursts down to the configured sustained rate.
    """

    def __init__(self, requests_per_second: float, burst_capacity: float | None = None) -> None:
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be > 0.")
        effective_capacity = burst_capacity if burst_capacity is not None else requests_per_second
        if effective_capacity <= 0:
            raise ValueError("burst_capacity must be > 0.")
        self._rate = requests_per_second
        self._capacity = effective_capacity
        self._tokens = effective_capacity
        self._updated_at = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> None:
        """Block, without holding the lock while sleeping, until `tokens` are available."""
        if tokens <= 0:
            raise ValueError("tokens must be > 0.")
        if tokens > self._capacity:
            raise ValueError(
                f"Requested {tokens} tokens exceeds the bucket capacity of {self._capacity}."
            )
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self._updated_at
                self._updated_at = now
                self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                deficit = tokens - self._tokens
                wait_time = deficit / self._rate
            await asyncio.sleep(wait_time)

    async def __aenter__(self) -> "TokenBucketRateLimiter":
        await self.acquire()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None
