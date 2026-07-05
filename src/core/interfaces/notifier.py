"""
ABC for outbound notification channels.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from src.core.domain.entities.signal import Signal


class Notifier(ABC):
    """Contract for delivering signal notifications and plain messages to
    users over an outbound channel (Telegram, email, push, etc.)."""

    @abstractmethod
    async def send_signal(self, user_id: str, signal: Signal) -> bool:
        """Deliver `signal` to `user_id`.

        Returns True on successful delivery, False if delivery failed in a
        recoverable way (e.g. the user blocked the bot).
        """
        raise NotImplementedError

    @abstractmethod
    async def send_message(self, user_id: str, text: str) -> bool:
        """Deliver a plain-text message to `user_id`. Returns True on success."""
        raise NotImplementedError

    @abstractmethod
    async def broadcast_signal(self, user_ids: Sequence[str], signal: Signal) -> int:
        """Deliver `signal` to every user in `user_ids`, returning the number
        of successful deliveries."""
        raise NotImplementedError
