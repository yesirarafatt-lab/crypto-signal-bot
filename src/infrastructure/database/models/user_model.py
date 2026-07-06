"""
SQLAlchemy ORM model: user.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.entities.user import User, UserRole
from src.infrastructure.database.base import Base, TimestampMixin


class UserModel(Base, TimestampMixin):
    """Persistence model for `User`."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    telegram_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=UserRole.USER.value)
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def to_entity(self) -> User:
        """Map this row to the `User` domain entity."""
        return User(
            created_at=self.created_at,
            id=self.id,
            telegram_id=self.telegram_id,
            username=self.username,
            email=self.email,
            hashed_password=self.hashed_password,
            role=UserRole(self.role),
            is_banned=self.is_banned,
        )

    @classmethod
    def from_entity(cls, entity: User) -> "UserModel":
        """Build a new row from a `User` domain entity."""
        return cls(
            id=entity.id,
            telegram_id=entity.telegram_id,
            username=entity.username,
            email=entity.email,
            hashed_password=entity.hashed_password,
            role=entity.role.value,
            is_banned=entity.is_banned,
            created_at=entity.created_at,
        )

    def apply_entity(self, entity: User) -> None:
        """Update this row's mutable fields in place from `entity`."""
        self.telegram_id = entity.telegram_id
        self.username = entity.username
        self.email = entity.email
        self.hashed_password = entity.hashed_password
        self.role = entity.role.value
        self.is_banned = entity.is_banned
