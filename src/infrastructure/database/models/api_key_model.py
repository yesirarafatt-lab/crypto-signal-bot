"""
SQLAlchemy ORM model: api_key.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base, TimestampMixin


class ApiKeyModel(Base, TimestampMixin):
    """An exchange API credential set belonging to a user.

    This is an infrastructure-only concern with no corresponding core
    domain entity; secrets are stored already encrypted at rest by
    `src.infrastructure.security`, never in plaintext.
    """

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exchange_name: Mapped[str] = mapped_column(String(50), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    encrypted_api_secret: Mapped[str] = mapped_column(String(1024), nullable=False)
    encrypted_passphrase: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
