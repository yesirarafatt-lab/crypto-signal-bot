"""
Risk score value object (0-100) with factor breakdown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType

from src.core.exceptions.validation_exceptions import OutOfRangeError


@dataclass(frozen=True, slots=True)
class RiskScore:
    """A 0-100 risk rating, optionally broken down by contributing factor
    (e.g. {"volatility": 30.0, "liquidity": 15.0, "correlation": 10.0})."""

    value: float
    factors: MappingProxyType[str, float] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 100.0):
            raise OutOfRangeError(f"RiskScore must be within [0, 100], got {self.value}.")
        for factor_name, factor_value in self.factors.items():
            if not (0.0 <= factor_value <= 100.0):
                raise OutOfRangeError(
                    f"RiskScore factor '{factor_name}' must be within [0, 100], "
                    f"got {factor_value}."
                )
        if not isinstance(self.factors, MappingProxyType):
            object.__setattr__(self, "factors", MappingProxyType(dict(self.factors)))

    @property
    def is_high_risk(self) -> bool:
        """True when the score meets a commonly used high-risk threshold (>= 70)."""
        return self.value >= 70.0

    def __lt__(self, other: "RiskScore") -> bool:
        return self.value < other.value

    def __le__(self, other: "RiskScore") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "RiskScore") -> bool:
        return self.value > other.value

    def __ge__(self, other: "RiskScore") -> bool:
        return self.value >= other.value

    def __str__(self) -> str:
        return f"{self.value:.1f}"
