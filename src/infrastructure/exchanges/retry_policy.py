"""
Tenacity-based retry/backoff decorator for transient exchange errors.
"""

from __future__ import annotations

import logging
from typing import Awaitable, Callable, Final, TypeVar

import ccxt
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

_T = TypeVar("_T")

# Transient ccxt errors worth retrying: network hiccups, timeouts, temporary
# exchange unavailability, and rate-limit rejections. Authentication, invalid
# order, insufficient funds, etc. are permanent and must not be retried.
_RETRYABLE_CCXT_EXCEPTIONS: Final[tuple[type[Exception], ...]] = (
    ccxt.NetworkError,
    ccxt.RequestTimeout,
    ccxt.ExchangeNotAvailable,
    ccxt.DDoSProtection,
    ccxt.RateLimitExceeded,
)


class RetryPolicy:
    """Retries transient exchange operations with exponential backoff.

    Wraps an arbitrary zero-argument async callable and retries it, using
    tenacity's `AsyncRetrying`, whenever it raises one of the transient
    `ccxt` exception types. All other exceptions propagate immediately.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_wait_seconds: float = 1.0,
        max_wait_seconds: float = 10.0,
        exponential_base: float = 2.0,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1.")
        if initial_wait_seconds <= 0:
            raise ValueError("initial_wait_seconds must be > 0.")
        if max_wait_seconds < initial_wait_seconds:
            raise ValueError("max_wait_seconds must be >= initial_wait_seconds.")
        self._max_attempts = max_attempts
        self._initial_wait_seconds = initial_wait_seconds
        self._max_wait_seconds = max_wait_seconds
        self._exponential_base = exponential_base

    async def execute(
        self,
        operation: Callable[[], Awaitable[_T]],
        *,
        operation_name: str = "exchange_operation",
    ) -> _T:
        """Execute `operation`, retrying on transient ccxt errors with exponential backoff."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential(
                multiplier=self._initial_wait_seconds,
                max=self._max_wait_seconds,
                exp_base=self._exponential_base,
            ),
            retry=retry_if_exception_type(_RETRYABLE_CCXT_EXCEPTIONS),
            reraise=True,
        ):
            with attempt:
                attempt_number = attempt.retry_state.attempt_number
                if attempt_number > 1:
                    logger.warning(
                        "Retrying %s (attempt %d/%d).",
                        operation_name,
                        attempt_number,
                        self._max_attempts,
                    )
                return await operation()

        # Unreachable: AsyncRetrying either returns via the block above or
        # raises (reraise=True). Present only to satisfy static type checkers.
        raise RuntimeError(f"Retry loop for '{operation_name}' exited without a result.")
