"""
Concrete ExchangeClient using ccxt.async_support (Bybit, spot + futures).
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import Any, Awaitable, Callable, Mapping, Sequence, TypeVar

import ccxt
import ccxt.async_support as ccxt_async

from src.config.settings import ExchangeSettings
from src.core.exceptions.exchange_exceptions import (
    ExchangeAuthenticationError,
    ExchangeConnectionError,
    ExchangeError,
    ExchangeNotAvailableError,
    ExchangeRateLimitError,
    ExchangeTimeoutError,
    InsufficientFundsError,
    InvalidOrderError,
    InvalidSymbolError,
    OrderNotFoundError,
)
from src.core.interfaces.exchange_client import ExchangeClient
from src.core.interfaces.market_data_provider import MarketDataProvider
from src.infrastructure.exchanges.rate_limiter import TokenBucketRateLimiter
from src.infrastructure.exchanges.retry_policy import RetryPolicy
from src.infrastructure.exchanges.symbol_normalizer import SymbolNormalizer

logger = logging.getLogger(__name__)

_T = TypeVar("_T")

# ccxt's unified `options.defaultType` values for Bybit: spot markets use
# "spot"; USDT-margined linear perpetual futures use "swap".
_BYBIT_MARKET_TYPE_MAP: Mapping[str, str] = {"spot": "spot", "futures": "swap"}


class CCXTExchangeClient(ExchangeClient, MarketDataProvider):
    """Bybit exchange client built on ccxt.async_support, spot + futures capable.

    All configuration is read from the injected `ExchangeSettings` instance,
    which callers obtain via `get_settings().exchange` (typically through
    `ExchangeFactory`). Every outbound call is rate-limited, retried on
    transient failures, and has its `ccxt` exceptions translated into this
    project's domain exceptions before they leave the infrastructure layer.
    """

    def __init__(
        self,
        settings: ExchangeSettings,
        symbol_normalizer: SymbolNormalizer,
        retry_policy: RetryPolicy,
        rate_limiter: TokenBucketRateLimiter,
    ) -> None:
        if settings.name != "bybit":
            raise ExchangeError(
                f"CCXTExchangeClient currently supports only 'bybit', got '{settings.name}'."
            )
        self._settings = settings
        self._symbol_normalizer = symbol_normalizer
        self._retry_policy = retry_policy
        self._rate_limiter = rate_limiter
        self._exchange: ccxt_async.bybit | None = None

    async def connect(self) -> None:
        """Create and configure the underlying ccxt Bybit client. Idempotent."""
        if self._exchange is not None:
            return
        exchange = ccxt_async.bybit(
            {
                "apiKey": self._settings.api_key.get_secret_value(),
                "secret": self._settings.api_secret.get_secret_value(),
                # We enforce our own outbound rate limiting via
                # TokenBucketRateLimiter, so ccxt's built-in limiter is disabled
                # to avoid double-throttling requests.
                "enableRateLimit": False,
                "timeout": self._settings.request_timeout_seconds * 1000,
                "options": {
                    "defaultType": _BYBIT_MARKET_TYPE_MAP[self._settings.default_market_type]
                },
            }
        )
        if self._settings.use_testnet:
            exchange.set_sandbox_mode(True)
        self._exchange = exchange
        logger.info(
            "Connected to Bybit (%s, market_type=%s).",
            "testnet" if self._settings.use_testnet else "mainnet",
            self._settings.default_market_type,
        )

    async def close(self) -> None:
        """Close the underlying ccxt client and release its network resources."""
        if self._exchange is not None:
            await self._exchange.close()
            self._exchange = None
            logger.info("Closed Bybit exchange connection.")

    async def __aenter__(self) -> "CCXTExchangeClient":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    def _require_exchange(self) -> ccxt_async.bybit:
        if self._exchange is None:
            raise ExchangeConnectionError("Exchange client is not connected. Call connect() first.")
        return self._exchange

    async def _call(
        self,
        operation_name: str,
        func: Callable[..., Awaitable[_T]],
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        """Rate-limit, retry, and run a ccxt call, translating any ccxt error raised."""

        async def _bound_operation() -> _T:
            await self._rate_limiter.acquire()
            return await func(*args, **kwargs)

        try:
            return await self._retry_policy.execute(_bound_operation, operation_name=operation_name)
        except ccxt.AuthenticationError as exc:
            raise ExchangeAuthenticationError(str(exc)) from exc
        except ccxt.InsufficientFunds as exc:
            raise InsufficientFundsError(str(exc)) from exc
        except ccxt.OrderNotFound as exc:
            raise OrderNotFoundError(str(exc)) from exc
        except ccxt.InvalidOrder as exc:
            raise InvalidOrderError(str(exc)) from exc
        except ccxt.BadSymbol as exc:
            raise InvalidSymbolError(str(exc)) from exc
        except ccxt.RateLimitExceeded as exc:
            raise ExchangeRateLimitError(str(exc)) from exc
        except ccxt.RequestTimeout as exc:
            raise ExchangeTimeoutError(str(exc)) from exc
        except ccxt.ExchangeNotAvailable as exc:
            raise ExchangeNotAvailableError(str(exc)) from exc
        except ccxt.NetworkError as exc:
            raise ExchangeConnectionError(str(exc)) from exc
        except ccxt.ExchangeError as exc:
            raise ExchangeError(str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 - guarantee no raw exchange error escapes.
            raise ExchangeError(f"Unexpected error during '{operation_name}': {exc}") from exc

    async def test_connection(self) -> bool:
        """Verify connectivity and credentials by requesting the exchange server time."""
        exchange = self._require_exchange()
        await self._call("test_connection", exchange.fetch_time)
        return True

    async def load_markets(self, reload: bool = False) -> Mapping[str, Any]:
        exchange = self._require_exchange()
        return await self._call("load_markets", exchange.load_markets, reload)

    async def fetch_balance(self) -> Mapping[str, Any]:
        exchange = self._require_exchange()
        return await self._call("fetch_balance", exchange.fetch_balance)

    async def fetch_ticker(self, symbol: str) -> Mapping[str, Any]:
        exchange = self._require_exchange()
        ccxt_symbol = self._symbol_normalizer.to_ccxt(symbol, self._settings.default_market_type)
        return await self._call("fetch_ticker", exchange.fetch_ticker, ccxt_symbol)

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: int | None = None,
        limit: int | None = None,
    ) -> Sequence[Sequence[float]]:
        self._symbol_normalizer.validate_timeframe(timeframe)
        exchange = self._require_exchange()
        ccxt_symbol = self._symbol_normalizer.to_ccxt(symbol, self._settings.default_market_type)
        return await self._call(
            "fetch_ohlcv", exchange.fetch_ohlcv, ccxt_symbol, timeframe, since, limit
        )
