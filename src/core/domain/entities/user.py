"""
User entity (Telegram + dashboard identity).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.core.exceptions.validation_exceptions import InvalidValueError


class UserRole(str, Enum):
    """Authorization role, shared by the Telegram bot and dashboard API."""

    USER = "user"
    ADMIN = "admin"

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True)
class User:
    """A user identity, reachable via Telegram and/or the dashboard.

    `hashed_password` and `email` are optional since a user may only ever
    interact through Telegram and never register for dashboard access.
    Password hashing itself is an infrastructure concern; this entity only
    stores the already-hashed value.
    """

    created_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    telegram_id: int | None = None
    username: str | None = None
    email: str | None = None
    hashed_password: str | None = None
    role: UserRole = UserRole.USER
    is_banned: bool = False

    def __post_init__(self) -> None:
        if self.telegram_id is None and self.email is None:
            raise InvalidValueError(
                "A User must have at least one identity: telegram_id or email."
            )

    @property
    def is_admin(self) -> bool:
        """True if this user has administrative privileges."""
        return self.role is UserRole.ADMIN

    def ban(self) -> None:
        """Ban this user, revoking bot/dashboard access."""
        self.is_banned = True

    def unban(self) -> None:
        """Lift a ban on this user."""
        self.is_banned = False
