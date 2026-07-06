"""
Async engine + sessionmaker + get_db_session dependency provider.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Return the process-wide async SQLAlchemy engine, created lazily on
    first use and cached for the lifetime of the process."""
    db_settings = get_settings().database
    return create_async_engine(
        str(db_settings.url),
        echo=db_settings.echo_sql,
        pool_size=db_settings.pool_size,
        max_overflow=db_settings.max_overflow,
        pool_timeout=db_settings.pool_timeout_seconds,
        pool_recycle=db_settings.pool_recycle_seconds,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide async session factory, bound to `get_engine()`."""
    return async_sessionmaker(bind=get_engine(), expire_on_commit=False, autoflush=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Request-scoped `AsyncSession` dependency (e.g. for FastAPI `Depends`).

    Commits on clean exit, rolls back and re-raises on any exception, and
    always closes the session afterwards.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    """Dispose of the process-wide engine's connection pool.

    Call during application shutdown to close all pooled connections
    cleanly (e.g. from a FastAPI lifespan handler or bot shutdown hook).
    """
    await get_engine().dispose()
