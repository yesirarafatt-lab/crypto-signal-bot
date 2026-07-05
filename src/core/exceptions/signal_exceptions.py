"""
Signal generation exception hierarchy.
"""

from __future__ import annotations


class SignalError(Exception):
    """Base class for all signal-related domain exceptions."""


class InvalidSignalError(SignalError):
    """Raised when a signal's internal data violates a domain invariant."""


class SignalNotFoundError(SignalError):
    """Raised when a referenced signal cannot be located."""


class DuplicateSignalError(SignalError):
    """Raised when a signal would duplicate an existing active signal for the same
    symbol and timeframe, violating the one-active-signal-per-symbol rule."""


class SignalExpiredError(SignalError):
    """Raised when an operation is attempted on a signal past its validity window."""


class SignalGenerationError(SignalError):
    """Raised when the signal generation pipeline fails to produce a valid signal."""
