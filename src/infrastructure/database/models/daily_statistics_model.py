"""
SQLAlchemy ORM model: daily_statistics.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.base import Base, TimestampMixin


class DailyStatisticsModel(Base, TimestampMixin):
    """A daily rollup of signal/trade performance, precomputed for fast
    dashboard and reporting queries. No corresponding core domain entity;
    this is a derived, infrastructure-only reporting concern."""

    __tablename__ = "daily_statistics"

    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    total_signals: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    win_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_pnl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_pnl_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_r_multiple: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    best_trade_pnl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    worst_trade_pnl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
