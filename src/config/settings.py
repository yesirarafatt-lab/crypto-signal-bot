"""
Application configuration.

Single source of truth for all runtime configuration. Every other module
obtains configuration exclusively through `get_settings()` — no module
reads `os.environ` directly.

Place this file at: src/config/settings.py
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = ".env"


class TelegramSettings(BaseSettings):
    """Telegram Bot configuration (python-telegram-bot v22)."""

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_", env_file=_ENV_FILE, extra="ignore")

    bot_token: SecretStr = Field(..., description="Bot token from @BotFather.")
    admin_ids: list[int] = Field(default_factory=list, description="Telegram user IDs with admin access.")
    use_webhook: bool = Field(default=False, description="Webhook mode instead of long polling.")
    webhook_url: str | None = Field(default=None, description="Public HTTPS webhook URL.")
    webhook_secret: SecretStr | None = Field(default=None, description="Secret validating webhook requests.")
    webhook_listen_host: str = Field(default="0.0.0.0", description="Host the webhook server binds to.")  # noqa: S104
    webhook_listen_port: int = Field(default=8443, ge=1, le=65535, description="Webhook server port.")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> list[int]:
        if isinstance(value, str):
            return [int(v.strip()) for v in value.split(",") if v.strip()]
        if isinstance(value, list):
            return [int(v) for v in value]
        return []

    @model_validator(mode="after")
    def _validate_webhook_config(self) -> TelegramSettings:
        if self.use_webhook:
            if not self.webhook_url:
                raise ValueError("TELEGRAM_WEBHOOK_URL is required when TELEGRAM_USE_WEBHOOK=true.")
            if not self.webhook_url.startswith("https://"):
                raise ValueError("TELEGRAM_WEBHOOK_URL must start with https://.")
            if not self.webhook_secret:
                raise ValueError("TELEGRAM_WEBHOOK_SECRET is required when TELEGRAM_USE_WEBHOOK=true.")
        return self


class ExchangeSettings(BaseSettings):
    """CCXT exchange credentials. Supports binance, bybit, okx, bitget."""

    model_config = SettingsConfigDict(env_prefix="EXCHANGE_", env_file=_ENV_FILE, extra="ignore")

    name: Literal["binance", "bybit", "okx", "bitget"] = Field(default="binance")
    api_key: SecretStr = Field(..., description="Exchange API key (trading permissions only, no withdrawal).")
    api_secret: SecretStr = Field(..., description="Exchange API secret.")
    api_passphrase: SecretStr | None = Field(
        default=None, description="Required by OKX/Bitget; unused by Binance/Bybit."
    )
    use_testnet: bool = Field(default=False)
    default_market_type: Literal["spot", "futures"] = Field(default="futures")
    request_timeout_seconds: int = Field(default=15, ge=1, le=60)
    rate_limit_requests_per_second: float = Field(
        default=10.0, gt=0, le=100, description="Token-bucket cap for outbound exchange requests."
    )

    @model_validator(mode="after")
    def _validate_passphrase_requirement(self) -> ExchangeSettings:
        if self.name in {"okx", "bitget"} and self.api_passphrase is None:
            raise ValueError(f"EXCHANGE_API_PASSPHRASE is required for exchange '{self.name}'.")
        return self


class TradingViewSettings(BaseSettings):
    """TradingView webhook alert ingestion configuration."""

    model_config = SettingsConfigDict(env_prefix="TRADINGVIEW_", env_file=_ENV_FILE, extra="ignore")

    webhook_secret: SecretStr = Field(..., description="Shared secret required in inbound TradingView payloads.")
    webhook_path: str = Field(default="/api/v1/webhooks/tradingview")


class OpenAISettings(BaseSettings):
    """OpenAI API configuration for AI-generated signal reasoning."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", env_file=_ENV_FILE, extra="ignore")

    enabled: bool = Field(default=False, description="If False, reasoning falls back to rule-based text only.")
    api_key: SecretStr | None = Field(default=None)
    model: str = Field(default="gpt-4o-mini")
    max_tokens: int = Field(default=500, ge=1, le=4096)
    request_timeout_seconds: int = Field(default=30, ge=1, le=120)

    @model_validator(mode="after")
    def _validate_api_key_present(self) -> OpenAISettings:
        if self.enabled and self.api_key is None:
            raise ValueError("OPENAI_API_KEY is required when OPENAI_ENABLED=true.")
        return self


class DatabaseSettings(BaseSettings):
    """PostgreSQL configuration (async SQLAlchemy engine)."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_", env_file=_ENV_FILE, extra="ignore")

    url: PostgresDsn = Field(..., description="postgresql+asyncpg://user:pass@host:5432/dbname")
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    pool_timeout_seconds: int = Field(default=30, ge=1, le=120)
    pool_recycle_seconds: int = Field(default=1800, ge=60)
    echo_sql: bool = Field(default=False)

    @field_validator("url")
    @classmethod
    def _require_asyncpg_driver(cls, value: PostgresDsn) -> PostgresDsn:
        if value.scheme != "postgresql+asyncpg":
            raise ValueError(
                f"DATABASE_URL must use the 'postgresql+asyncpg' scheme, got '{value.scheme}'."
            )
        return value


class RedisSettings(BaseSettings):
    """Redis configuration — caching, rate limiting, pub/sub."""

    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=_ENV_FILE, extra="ignore")

    url: RedisDsn = Field(default=RedisDsn("redis://localhost:6379/0"))
    cache_ttl_seconds: int = Field(default=60, ge=1)
    max_connections: int = Field(default=50, ge=1, le=500)


class LoggingSettings(BaseSettings):
    """Application logging configuration. Consumed by config/logger.py."""

    model_config = SettingsConfigDict(env_prefix="LOG_", env_file=_ENV_FILE, extra="ignore")

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    json_console: bool = Field(default=False, description="Emit JSON on stdout instead of colored text.")
    json_file: bool = Field(default=True, description="Emit JSON in rotating log files.")
    log_dir: str = Field(default="logs")
    backup_count_days: int = Field(default=30, ge=1, le=365)
    enable_file_logging: bool = Field(default=True)
    persist_to_database: bool = Field(
        default=False, description="Also write ERROR+ log records to the log_entries table."
    )
    sentry_dsn: SecretStr | None = Field(default=None)

    @field_validator("level", mode="before")
    @classmethod
    def _normalize_level(cls, value: object) -> object:
        return value.upper() if isinstance(value, str) else value

    def to_python_level(self) -> int:
        return getattr(logging, self.level)


class RiskManagementSettings(BaseSettings):
    """Risk rules enforced by the Risk Management Engine before any signal is published."""

    model_config = SettingsConfigDict(env_prefix="RISK_", env_file=_ENV_FILE, extra="ignore")

    max_risk_per_trade_percent: float = Field(default=1.0, gt=0, le=100)
    default_stop_loss_percent: float = Field(default=2.0, gt=0, le=100)
    default_take_profit_percent: float = Field(default=4.0, gt=0, le=100)
    atr_stop_loss_multiplier: float = Field(default=1.5, gt=0, le=10)
    min_risk_reward_ratio: float = Field(default=1.5, gt=0)
    min_confidence_score: float = Field(default=70.0, ge=0, le=100)
    max_open_signals_per_symbol: int = Field(default=1, ge=1)
    max_open_positions_total: int = Field(default=10, ge=1)
    signal_cooldown_minutes: int = Field(default=15, ge=0)
    max_daily_signals: int = Field(default=50, ge=1)
    daily_loss_limit_percent: float = Field(
        default=5.0, gt=0, le=100, description="Max % of equity lost in a day before new signals halt."
    )
    max_consecutive_losses: int = Field(
        default=4, ge=1, description="Consecutive losing trades before a cooldown is triggered."
    )
    consecutive_loss_cooldown_hours: int = Field(default=12, ge=1, le=168)
    break_even_trigger_r_multiple: float = Field(
        default=1.0, gt=0, description="Move SL to entry once price reaches this R-multiple in profit."
    )
    trailing_stop_activation_r_multiple: float = Field(default=1.5, gt=0)
    partial_take_profit_levels: list[float] = Field(
        default_factory=lambda: [0.5, 0.3, 0.2],
        description="Position size fractions closed at TP1/TP2/TP3; must sum to 1.0.",
    )

    @field_validator("partial_take_profit_levels", mode="before")
    @classmethod
    def _parse_tp_levels(cls, value: object) -> object:
        if isinstance(value, str):
            return [float(v.strip()) for v in value.split(",") if v.strip()]
        return value

    @model_validator(mode="after")
    def _validate_risk_consistency(self) -> RiskManagementSettings:
        if self.default_take_profit_percent <= self.default_stop_loss_percent:
            raise ValueError(
                "RISK_DEFAULT_TAKE_PROFIT_PERCENT must exceed RISK_DEFAULT_STOP_LOSS_PERCENT."
            )
        total = sum(self.partial_take_profit_levels)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"RISK_PARTIAL_TAKE_PROFIT_LEVELS must sum to 1.0, got {total}."
            )
        return self


class DashboardAuthSettings(BaseSettings):
    """JWT authentication configuration for the Dashboard API (web dashboard login)."""

    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=_ENV_FILE, extra="ignore")

    jwt_secret_key: SecretStr = Field(..., description="Secret used to sign JWTs. Must be >= 32 random chars.")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=90)

    @field_validator("jwt_secret_key")
    @classmethod
    def _validate_secret_strength(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("AUTH_JWT_SECRET_KEY must be at least 32 characters long.")
        return value


class CorsSettings(BaseSettings):
    """CORS configuration for the Dashboard API, consumed by the React web dashboard."""

    model_config = SettingsConfigDict(env_prefix="CORS_", env_file=_ENV_FILE, extra="ignore")

    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


class Settings(BaseSettings):
    """Root settings object. Instantiate exclusively via get_settings()."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore", case_sensitive=False)

    environment: Literal["development", "staging", "production"] = Field(default="development")
    app_name: str = Field(default="AI Crypto Signal Bot")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    telegram: TelegramSettings = Field(default_factory=TelegramSettings)
    exchange: ExchangeSettings = Field(default_factory=ExchangeSettings)
    tradingview: TradingViewSettings = Field(default_factory=TradingViewSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    risk: RiskManagementSettings = Field(default_factory=RiskManagementSettings)
    auth: DashboardAuthSettings = Field(default_factory=DashboardAuthSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)

    @model_validator(mode="after")
    def _validate_production_safety(self) -> Settings:
        if self.environment == "production":
            if self.debug:
                raise ValueError("DEBUG must be False when ENVIRONMENT=production.")
            if self.exchange.use_testnet:
                raise ValueError("EXCHANGE_USE_TESTNET must be False when ENVIRONMENT=production.")
            if self.logging.level == "DEBUG":
                raise ValueError("LOG_LEVEL must not be DEBUG when ENVIRONMENT=production.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached, process-wide, validated Settings instance."""
    return Settings()
