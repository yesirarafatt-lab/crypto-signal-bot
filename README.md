# AI Crypto Signal Bot

Production-ready AI-powered crypto signal generation and Telegram notification
system, built with Clean Architecture in Python 3.12.

> **Status:** Professional project structure scaffolded. Core configuration
> (`pyproject.toml`, `src/config/settings.py`) is fully implemented. All other
> modules are stubbed with descriptive docstrings and are being filled in
> file-by-file — see the module status table below.

## Features

- Multi-exchange market data via CCXT (Binance, Bybit, OKX, Bitget — spot & futures)
- Technical Indicator Engine (EMA, SMA, VWAP, RSI, MACD, ADX, ATR, Supertrend, Bollinger Bands, Volume Profile, Donchian, Ichimoku)
- Smart Money Concept Engine (Order Blocks, Breaker Blocks, FVG, Liquidity Sweeps/Grabs, BOS/CHoCH, Premium/Discount, Mitigation, Displacement, Institutional Candles)
- AI Signal Engine combining trend, indicator, and SMC confluence into BUY/SELL/NO_TRADE with confidence + risk scoring and reasoning
- Risk Management Engine (dynamic sizing, ATR stop-loss, daily loss limits, consecutive-loss cooldown, trailing stop, break-even, partial take-profit)
- Telegram Bot on `python-telegram-bot` v22 (`/start`, `/help`, `/status`, `/settings`, `/signal`, `/history`, `/admin`)
- FastAPI Dashboard API with JWT auth and Swagger docs
- React + TailwindCSS web dashboard with TradingView embeds and dark mode
- PostgreSQL + SQLAlchemy (async) + Alembic migrations
- Docker Compose deployment behind Nginx
- GitHub Actions CI/CD with automatic semantic versioning

## Quickstart

```bash
git clone <repo-url> crypto-signal-bot
cd crypto-signal-bot
cp .env.example .env        # fill in your credentials
make dev-install
make migrate
make run-api                # in one terminal
make run-bot                # in another terminal
make run-scheduler          # in another terminal
```

Or via Docker:

```bash
cp .env.example .env
make docker-up
```

## Documentation

| Guide | Purpose |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Folder structure, data flow, module dependency diagram |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Local setup, prerequisites, first run |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Full `.env` variable reference |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Docker Compose, Nginx, CI/CD release flow |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common errors and fixes, by module |
| [docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md) | Risk config guidance, strategy tuning |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Swagger UI, auth flow, example requests |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branching, commits, PR process |
| [SECURITY.md](SECURITY.md) | Vulnerability disclosure policy |

## Project Structure

```
crypto-signal-bot/
├── src/
│   ├── config/            # Settings, logging
│   ├── core/               # Entities, value objects, interfaces, exceptions (zero deps)
│   ├── infrastructure/       # Exchange, database, cache, security, Telegram, AI adapters
│   ├── application/            # Services, strategies, indicators, SMC, analyzers, use cases
│   ├── api/                       # FastAPI dashboard API
│   ├── scheduler/                    # APScheduler background jobs
│   ├── utils/                          # Shared helpers
│   └── main.py                          # Entry point
├── tests/                  # unit/ + integration/, mirrors src/ layout
├── alembic/                  # DB migrations
├── docker/                     # Dockerfiles, Compose, Nginx, entrypoints
├── web-dashboard/                # React + TailwindCSS frontend
├── .github/workflows/               # CI/CD
├── docs/                               # Full documentation set
└── pyproject.toml                        # Dependencies + tool config (ruff, mypy, pytest)
```

Full detail in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Module Implementation Status

| Module | Status |
|---|---|
| Configuration (`config/settings.py`) | ✅ Implemented |
| Logging (`config/logger.py`) | ⬜ Scaffolded |
| Core domain (entities, VOs, interfaces, exceptions) | ⬜ Scaffolded |
| Database (models, repositories, Alembic) | ⬜ Scaffolded |
| Exchange module (CCXT client, factory, rate limiter, retry) | ⬜ Scaffolded |
| Market Data module | ⬜ Scaffolded |
| Indicator Engine | ⬜ Scaffolded |
| Smart Money Concept Engine | ⬜ Scaffolded |
| AI Signal Engine | ⬜ Scaffolded |
| Risk Management Engine | ⬜ Scaffolded |
| Telegram Bot (PTB v22) | ⬜ Scaffolded |
| Dashboard API (FastAPI) | ⬜ Scaffolded |
| Web Dashboard (React) | ⬜ Scaffolded |
| Testing Suite | ⬜ Scaffolded |
| Docker Deployment | ⬜ Scaffolded |
| CI/CD | ⬜ Scaffolded |

Files are implemented one at a time, in dependency order, each verified
against the files before it — see chat history for the agreed build order.

## License

Proprietary — see [LICENSE](LICENSE).
