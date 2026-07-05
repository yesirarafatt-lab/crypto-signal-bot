"""
ABC for trading strategies feeding the signal aggregator.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from src.core.domain.entities.candle import Candle
from src.core.domain.entities.indicator_result import IndicatorResult


class IndicatorStrategy(ABC):
    """Contract for a single trading strategy (indicator-based, SMC-based, or
    composite) that evaluates candle history and produces a directional
    verdict for the strategy aggregator to combine with others."""

    @property
    @abstractmethod
    def name(self) -> str:
        """A unique, human-readable identifier for this strategy."""
        raise NotImplementedError

    @property
    @abstractmethod
    def min_candles_required(self) -> int:
        """The minimum number of candles this strategy needs to produce a
        meaningful result. Callers must not invoke `evaluate` with fewer."""
        raise NotImplementedError

    @abstractmethod
    async def evaluate(self, candles: Sequence[Candle]) -> IndicatorResult:
        """Evaluate `candles` (oldest first) and return this strategy's verdict.

        Raises:
            ValueError: if fewer than `min_candles_required` candles are given.
        """
        raise NotImplementedError
