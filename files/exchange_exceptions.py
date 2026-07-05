"""
Domain-level exceptions for the exchange infrastructure layer.

Every exception raised by code outside `src/infrastructure/exchanges/` that
originates from an exchange interaction must be one of these types. Raw
`ccxt` exceptions must never cross the infrastructure boundary; the
concrete exchange client is responsible for translating them here.
"""

from __future__ import annotations


class ExchangeError(Exception):
    """Base class for all exchange-related domain exceptions."""


class ExchangeConnectionError(ExchangeError):
    """Raised when the exchange cannot be reached (network failure, DNS, timeout)."""


class ExchangeAuthenticationError(ExchangeError):
    """Raised when API credentials are invalid, expired, or lack required permissions."""


class ExchangeRateLimitError(ExchangeError):
    """Raised when the exchange rejects a request because a rate limit was exceeded."""


class ExchangeNotAvailableError(ExchangeError):
    """Raised when the exchange, or a specific market on it, is temporarily unavailable."""


class ExchangeTimeoutError(ExchangeError):
    """Raised when a request to the exchange exceeds the configured timeout."""


class InsufficientFundsError(ExchangeError):
    """Raised when the account lacks sufficient balance for a requested operation."""


class InvalidOrderError(ExchangeError):
    """Raised when an order is rejected by the exchange due to invalid parameters."""


class OrderNotFoundError(InvalidOrderError):
    """Raised when a requested order cannot be located on the exchange."""


class InvalidSymbolError(ExchangeError):
    """Raised when a trading symbol is malformed, unknown, or not found on the exchange."""


class InvalidTimeframeError(ExchangeError):
    """Raised when an OHLCV timeframe is not supported by the exchange or normalizer."""
