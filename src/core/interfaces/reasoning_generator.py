"""
ABC for signal reasoning text generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from src.core.domain.value_objects.trade_decision import TradeDecision


class ReasoningGenerator(ABC):
    """Contract for producing a human-readable explanation of why a signal
    (or a NO_TRADE verdict) was generated, from the underlying analysis
    context assembled by the confluence analyzers."""

    @abstractmethod
    async def generate(
        self, direction: TradeDecision, analysis_context: Mapping[str, Any]
    ) -> str:
        """Produce a concise, human-readable reasoning string for `direction`,
        given the confluence/analyzer output in `analysis_context`.

        Implementations must never propagate provider or content-policy
        failures to the caller; on such failures they should fall back to a
        deterministic templated explanation instead, so signal generation is
        never blocked by an external reasoning provider being unavailable.
        """
        raise NotImplementedError
