"""
Open interest entity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.domain.value_objects.symbol import Symbol


@dataclass(slots=True)
class OpenInterest:
    """An open-interest snapshot for a symbol (total outstanding derivative
    contracts, typically denominated in the base asset or USD)."""

    symbol: Symbol
    value: float
    timestamp: datetime
