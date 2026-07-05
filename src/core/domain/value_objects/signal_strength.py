"""
Signal strength/confidence value object.
"""

from __future__ import annotations

from enum import Enum

from src.core.domain.value_objects.confidence_score import ConfidenceScore


class SignalStrength(str, Enum):
    """A coarse, human-readable classification of a signal's confidence level."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_confidence(cls, confidence: ConfidenceScore) -> "SignalStrength":
        """Bucket a ConfidenceScore into a SignalStrength classification."""
        value = confidence.value
        if value >= 90.0:
            return cls.VERY_STRONG
        if value >= 70.0:
            return cls.STRONG
        if value >= 50.0:
            return cls.MODERATE
        return cls.WEAK
