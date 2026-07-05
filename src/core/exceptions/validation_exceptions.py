"""
Input/domain validation exception hierarchy.
"""

from __future__ import annotations


class ValidationError(Exception):
    """Base class for all domain validation failures."""


class InvalidValueError(ValidationError):
    """Raised when a value fails a domain invariant (format, type, or business rule)."""


class OutOfRangeError(ValidationError):
    """Raised when a numeric value falls outside its permitted domain range."""


class MissingFieldError(ValidationError):
    """Raised when a required field is absent or empty."""
