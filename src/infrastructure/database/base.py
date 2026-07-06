"""
SQLAlchemy declarative base, naming convention, TimestampMixin.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Explicit naming convention so Alembic autogenerate produces stable,
# dialect-independent constraint/index names instead of driver-assigned ones.
_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model in the project."""

    metadata = MetaData(naming_convention=_NAMING_CONVENTION)


class TimestampMixin:
    """Adds server-managed `created_at`/`updated_at` timestamp columns.

    Both columns are populated by the database server (`func.now()`), not
    the application clock, so they stay correct regardless of app-server
    clock skew and remain accurate for rows inserted outside the ORM.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
