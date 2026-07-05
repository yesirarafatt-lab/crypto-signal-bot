"""
Entry zone value object (upper/lower bound).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.domain.value_objects.price import Price
from src.core.domain.value_objects.zone_range import ZoneRange
from src.core.exceptions.validation_exceptions import InvalidValueError


@dataclass(frozen=True, slots=True)
class EntryZone:
    """The price band within which a signal's entry should be filled.

    Wraps a `ZoneRange` and adds a preferred (optimal) entry price, which is
    typically the zone's midpoint but may be skewed toward one edge by the
    strategy that produced it.
    """

    range: ZoneRange
    preferred_entry: Price

    def __post_init__(self) -> None:
        if not self.range.contains(self.preferred_entry):
            raise InvalidValueError(
                f"Preferred entry {self.preferred_entry} lies outside entry zone {self.range}."
            )

    @property
    def upper_bound(self) -> Price:
        return self.range.top

    @property
    def lower_bound(self) -> Price:
        return self.range.bottom

    def contains(self, price: Price) -> bool:
        """True if `price` falls within the entry zone."""
        return self.range.contains(price)

    def __str__(self) -> str:
        return f"EntryZone{self.range} preferred={self.preferred_entry}"
