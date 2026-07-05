"""
Normalizes symbol formats between internal and per-exchange CCXT notation.
"""

from __future__ import annotations

import re
from typing import Final, Literal

from src.core.exceptions.exchange_exceptions import InvalidSymbolError, InvalidTimeframeError

# Internal notation is always "BASE/QUOTE", e.g. "BTC/USDT". Symbols without a
# separator (e.g. "BTCUSDT") are rejected as malformed.
_SYMBOL_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Z0-9]{2,20}/[A-Z0-9]{2,20}$")

_VALID_TIMEFRAMES: Final[frozenset[str]] = frozenset(
    {"1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"}
)

MarketType = Literal["spot", "futures"]


class SymbolNormalizer:
    """Validates internal symbols and converts them to/from CCXT-unified notation.

    Bybit (via ccxt) uses plain "BASE/QUOTE" for spot markets and
    "BASE/QUOTE:SETTLE" for linear (USDT-margined) perpetual futures.
    """

    def __init__(self, market_type: MarketType = "futures", settle_currency: str = "USDT") -> None:
        self._market_type: MarketType = market_type
        self._settle_currency = settle_currency

    def validate(self, symbol: str) -> None:
        """Raise InvalidSymbolError if `symbol` is not in internal "BASE/QUOTE" notation."""
        if not isinstance(symbol, str) or not _SYMBOL_PATTERN.match(symbol):
            raise InvalidSymbolError(
                f"Malformed symbol '{symbol}'. Expected internal notation 'BASE/QUOTE', "
                f"e.g. 'BTC/USDT'."
            )

    def to_ccxt(self, symbol: str, market_type: MarketType | None = None) -> str:
        """Convert an internal symbol to CCXT-unified notation for the given market type."""
        self.validate(symbol)
        effective_type: MarketType = market_type if market_type is not None else self._market_type
        if effective_type == "spot":
            return symbol
        if effective_type == "futures":
            base, quote = symbol.split("/")
            return f"{base}/{quote}:{self._settle_currency}"
        raise InvalidSymbolError(
            f"Unsupported market type '{effective_type}' while converting symbol '{symbol}'."
        )

    def from_ccxt(self, ccxt_symbol: str) -> str:
        """Convert a CCXT-unified symbol back to internal "BASE/QUOTE" notation."""
        if not isinstance(ccxt_symbol, str) or not ccxt_symbol:
            raise InvalidSymbolError(f"Malformed CCXT symbol '{ccxt_symbol}'.")
        base_quote = ccxt_symbol.split(":", 1)[0]
        self.validate(base_quote)
        return base_quote

    def validate_timeframe(self, timeframe: str) -> None:
        """Raise InvalidTimeframeError if `timeframe` is not a supported OHLCV interval."""
        if timeframe not in _VALID_TIMEFRAMES:
            raise InvalidTimeframeError(
                f"Unsupported timeframe '{timeframe}'. Valid values: {sorted(_VALID_TIMEFRAMES)}."
            )
