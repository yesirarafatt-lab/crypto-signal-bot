"""
Single indicator/strategy output entity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

from src.core.domain.value_objects.confidence_score import ConfidenceScore
from src.core.domain.value_objects.trade_decision import TradeDecision
from src.core.exceptions.validation_exceptions import InvalidValueError


@dataclass(slots=True)
class IndicatorResult:
    """The output of a single indicator or strategy evaluation.

    Produced by every `IndicatorStrategy` implementation and consumed by the
    confluence analyzers and strategy aggregator when building a final
    `Signal`. `metadata` carries strategy-specific supporting details (e.g.
    the RSI value, the ATR multiple used, or the detected SMC pattern) for
    use in reasoning generation and debugging.
    """

    name: str
    direction: TradeDecision
    confidence: ConfidenceScore
    timestamp: datetime
    metadata: MappingProxyType[str, object] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not self.name:
            raise InvalidValueError("IndicatorResult name must not be empty.")
        if not isinstance(self.metadata, MappingProxyType):
            self.metadata = MappingProxyType(dict(self.metadata))

    @property
    def is_actionable(self) -> bool:
        """True if this result carries a BUY/SELL verdict rather than NO_TRADE."""
        return self.direction.is_actionable

    def __str__(self) -> str:
        return f"IndicatorResult({self.name}: {self.direction}, confidence={self.confidence})"
