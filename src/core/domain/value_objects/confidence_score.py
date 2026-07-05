"""
Confidence score value object (0-100).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions.validation_exceptions import OutOfRangeError


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    """A 0-100 confidence rating produced by strategy/analyzer confluence scoring."""

    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.value <= 100.0):
            raise OutOfRangeError(
                f"ConfidenceScore must be within [0, 100], got {self.value}."
            )

    @property
    def is_high_confidence(self) -> bool:
        """True when the score meets a commonly used high-confidence threshold (>= 70)."""
        return self.value >= 70.0

    def __lt__(self, other: "ConfidenceScore") -> bool:
        return self.value < other.value

    def __le__(self, other: "ConfidenceScore") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "ConfidenceScore") -> bool:
        return self.value > other.value

    def __ge__(self, other: "ConfidenceScore") -> bool:
        return self.value >= other.value

    def __str__(self) -> str:
        return f"{self.value:.1f}"
