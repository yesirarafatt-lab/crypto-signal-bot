"""
Builds fully configured exchange clients from application settings.
"""

from __future__ import annotations

from typing import Final

from src.config.settings import ExchangeSettings, get_settings
from src.core.exceptions.exchange_exceptions import ExchangeError
from src.infrastructure.exchanges.ccxt_exchange_client import CCXTExchangeClient
from src.infrastructure.exchanges.rate_limiter import TokenBucketRateLimiter
from src.infrastructure.exchanges.retry_policy import RetryPolicy
from src.infrastructure.exchanges.symbol_normalizer import SymbolNormalizer

_SUPPORTED_EXCHANGES: Final[frozenset[str]] = frozenset({"bybit"})


class ExchangeFactory:
    """Assembles a `CCXTExchangeClient` and its collaborators from `ExchangeSettings`."""

    @staticmethod
    def create(settings: ExchangeSettings | None = None) -> CCXTExchangeClient:
        """Build a configured `CCXTExchangeClient`.

        Reads configuration exclusively from `get_settings().exchange` unless
        an explicit `ExchangeSettings` instance is supplied (e.g. for tests).
        """
        exchange_settings = settings if settings is not None else get_settings().exchange
        if exchange_settings.name not in _SUPPORTED_EXCHANGES:
            raise ExchangeError(
                f"Unsupported exchange '{exchange_settings.name}'. "
                f"Currently supported: {sorted(_SUPPORTED_EXCHANGES)}."
            )

        symbol_normalizer = SymbolNormalizer(market_type=exchange_settings.default_market_type)
        retry_policy = RetryPolicy()
        rate_limiter = TokenBucketRateLimiter(
            requests_per_second=exchange_settings.rate_limit_requests_per_second
        )

        return CCXTExchangeClient(
            settings=exchange_settings,
            symbol_normalizer=symbol_normalizer,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
        )


def create_exchange_client(settings: ExchangeSettings | None = None) -> CCXTExchangeClient:
    """Module-level convenience wrapper around `ExchangeFactory.create()`."""
    return ExchangeFactory.create(settings)
