.PHONY: install dev-install lint format type-check test test-unit test-integration coverage migrate run-api run-bot run-scheduler docker-up docker-down

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check src tests

format:
	ruff format src tests

type-check:
	mypy src

test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

coverage:
	pytest --cov --cov-report=html --cov-report=term-missing

migrate:
	alembic upgrade head

run-api:
	uvicorn api.app:create_app --factory --reload --host 0.0.0.0 --port 8000

run-bot:
	python -m src.main --service bot

run-scheduler:
	python -m src.main --service scheduler

docker-up:
	docker compose -f docker/docker-compose.yml up --build

docker-down:
	docker compose -f docker/docker-compose.yml down
