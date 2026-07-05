"""
Symbol value object (validated trading pair).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from src.core.exceptions.validation_exceptions import InvalidValueError

_SYMBOL_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Z0-9]{2,20}/[A-Z0-9]{2,20}$")


@dataclass(frozen=True, slots=True)
class Symbol:
    """An internal-notation trading pair, e.g. "BTC/USDT".

    Always validated on construction. Base and quote assets are exposed
    separately for callers that need them individually (e.g. balance lookups).
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not _SYMBOL_PATTERN.match(self.value):
            raise InvalidValueError(
                f"Malformed symbol '{self.value}'. Expected 'BASE/QUOTE', e.g. 'BTC/USDT'."
            )

    @property
    def base(self) -> str:
        """The base asset, e.g. 'BTC' in 'BTC/USDT'."""
        return self.value.split("/")[0]

    @property
    def quote(self) -> str:
        """The quote asset, e.g. 'USDT' in 'BTC/USDT'."""
        return self.value.split("/")[1]

    def __str__(self) -> str:
        return self.value
