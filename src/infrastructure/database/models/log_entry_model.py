"""
SQLAlchemy ORM model: log_entry.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base


class LogEntryModel(Base):
    """A structured application log record persisted for audit/debugging.

    No corresponding core domain entity; this is an infrastructure-only
    cross-cutting concern used by the logging subsystem.
    """

    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    logger_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
