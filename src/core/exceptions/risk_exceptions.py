"""
Risk management rule violation exceptions.
"""

from __future__ import annotations


class RiskError(Exception):
    """Base class for all risk-management domain exceptions."""


class RiskLimitExceededError(RiskError):
    """Raised when a generic configured risk limit would be exceeded."""


class DailyLossLimitExceededError(RiskError):
    """Raised when the account's daily loss limit has been reached or exceeded."""


class MaxOpenPositionsExceededError(RiskError):
    """Raised when opening a position would exceed the maximum allowed open positions."""


class InsufficientRiskRewardError(RiskError):
    """Raised when a proposed trade's risk/reward ratio is below the configured minimum."""


class ConsecutiveLossLimitExceededError(RiskError):
    """Raised when the maximum number of consecutive losing trades has been reached."""


class InvalidRiskParametersError(RiskError):
    """Raised when risk parameters (stop-loss, position size, etc.) are invalid or inconsistent."""
