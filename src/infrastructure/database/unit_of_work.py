"""
UnitOfWork pattern — transactional boundary across repositories.
"""

from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.repositories.account_state_repository_impl import (
    SqlAlchemyAccountStateRepository,
)
from src.infrastructure.database.repositories.api_key_repository_impl import (
    SqlAlchemyApiKeyRepository,
)
from src.infrastructure.database.repositories.candle_repository_impl import (
    SqlAlchemyCandleRepository,
)
from src.infrastructure.database.repositories.funding_rate_repository_impl import (
    SqlAlchemyFundingRateRepository,
)
from src.infrastructure.database.repositories.liquidation_repository_impl import (
    SqlAlchemyLiquidationRepository,
)
from src.infrastructure.database.repositories.log_repository_impl import SqlAlchemyLogRepository
from src.infrastructure.database.repositories.open_interest_repository_impl import (
    SqlAlchemyOpenInterestRepository,
)
from src.infrastructure.database.repositories.position_repository_impl import (
    SqlAlchemyPositionRepository,
)
from src.infrastructure.database.repositories.signal_delivery_repository_impl import (
    SqlAlchemySignalDeliveryRepository,
)
from src.infrastructure.database.repositories.signal_repository_impl import (
    SqlAlchemySignalRepository,
)
from src.infrastructure.database.repositories.statistics_repository_impl import (
    SqlAlchemyStatisticsRepository,
)
from src.infrastructure.database.repositories.subscription_repository_impl import (
    SqlAlchemySubscriptionRepository,
)
from src.infrastructure.database.repositories.trade_result_repository_impl import (
    SqlAlchemyTradeResultRepository,
)
from src.infrastructure.database.repositories.user_repository_impl import (
    SqlAlchemyUserRepository,
)
from src.infrastructure.database.session import get_session_factory


class UnitOfWork:
    """Groups one or more repository operations into a single atomic
    transaction, committing on clean exit and rolling back on error.

    Usage::

        async with UnitOfWork() as uow:
            signal = await uow.signals.get_by_id(signal_id)
            signal.activate()
            await uow.signals.update(signal)
            # commits automatically on successful exit

    Pass an existing `AsyncSession` (e.g. one supplied by `get_db_session()`
    in a FastAPI request) to join that session's transaction instead of
    opening a new one; in that case this `UnitOfWork` will not close the
    session on exit, leaving that to the owner of the session's lifecycle.
    """

    def __init__(self, session: AsyncSession | None = None) -> None:
        self._external_session = session
        self._session: AsyncSession | None = None

        self.signals: SqlAlchemySignalRepository
        self.positions: SqlAlchemyPositionRepository
        self.users: SqlAlchemyUserRepository
        self.account_state: SqlAlchemyAccountStateRepository
        self.candles: SqlAlchemyCandleRepository
        self.funding_rates: SqlAlchemyFundingRateRepository
        self.open_interest: SqlAlchemyOpenInterestRepository
        self.liquidations: SqlAlchemyLiquidationRepository
        self.subscriptions: SqlAlchemySubscriptionRepository
        self.trade_results: SqlAlchemyTradeResultRepository
        self.api_keys: SqlAlchemyApiKeyRepository
        self.logs: SqlAlchemyLogRepository
        self.statistics: SqlAlchemyStatisticsRepository
        self.signal_deliveries: SqlAlchemySignalDeliveryRepository

    async def __aenter__(self) -> "UnitOfWork":
        self._session = self._external_session or get_session_factory()()
        session = self._session
        self.signals = SqlAlchemySignalRepository(session)
        self.positions = SqlAlchemyPositionRepository(session)
        self.users = SqlAlchemyUserRepository(session)
        self.account_state = SqlAlchemyAccountStateRepository(session)
        self.candles = SqlAlchemyCandleRepository(session)
        self.funding_rates = SqlAlchemyFundingRateRepository(session)
        self.open_interest = SqlAlchemyOpenInterestRepository(session)
        self.liquidations = SqlAlchemyLiquidationRepository(session)
        self.subscriptions = SqlAlchemySubscriptionRepository(session)
        self.trade_results = SqlAlchemyTradeResultRepository(session)
        self.api_keys = SqlAlchemyApiKeyRepository(session)
        self.logs = SqlAlchemyLogRepository(session)
        self.statistics = SqlAlchemyStatisticsRepository(session)
        self.signal_deliveries = SqlAlchemySignalDeliveryRepository(session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            if self._external_session is None:
                await self._session.close()
            self._session = None

    async def commit(self) -> None:
        """Commit the current transaction without exiting the context."""
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction without exiting the context."""
        assert self._session is not None
        await self._session.rollback()
