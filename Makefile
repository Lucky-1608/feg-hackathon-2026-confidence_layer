.DEFAULT_GOAL := help

.PHONY: help venv install test test-unit test-adversarial test-load lint format \
	typecheck quality check all-checks compose-check db-up db-down db-migrate \
	db-revision infra-up infra-down run run-worker docker-up docker-down clean

VENV := .venv
BOOTSTRAP_PYTHON ?= python3
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
ALEMBIC := $(VENV)/bin/alembic
LOCUST := $(VENV)/bin/locust
PYTHON_PATHS := src tests alembic

help:
	@echo "Confidence Layer development commands"
	@echo "  make venv           Create the virtual environment and install dev dependencies"
	@echo "  make check          Run lint, formatting, type checks, and tests"
	@echo "  make format         Apply Ruff fixes and formatting"
	@echo "  make infra-up       Start local dependencies and apply migrations"
	@echo "  make run            Start the local API and demo UI"
	@echo "  make docker-up      Build and start the full Compose stack"
	@echo "  make clean          Remove generated Python and test caches"

venv:
	$(BOOTSTRAP_PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

install:
	$(PIP) install -e ".[dev]"

# --- Testing ---

test:
	$(PYTEST) tests -q --tb=short --ignore=tests/load --cov=confidence \
		--cov-branch --cov-report=term-missing:skip-covered --cov-report=xml \
		--cov-fail-under=75

test-unit:
	$(PYTEST) tests -q --tb=short --ignore=tests/load

test-adversarial:
	$(PYTEST) tests/test_adversarial.py tests/test_failure_injection.py \
		tests/test_properties.py -q --tb=long

test-load:
	$(LOCUST) -f tests/load/locustfile.py --headless -u 50 -r 10 \
		--run-time 30s --host http://localhost:8000

# --- Code quality ---

lint:
	$(RUFF) check $(PYTHON_PATHS)
	$(RUFF) format --check $(PYTHON_PATHS)

format:
	$(RUFF) check $(PYTHON_PATHS) --fix
	$(RUFF) format $(PYTHON_PATHS)

typecheck:
	$(MYPY) src --ignore-missing-imports

quality: lint typecheck

check: quality test

all-checks: check

# --- Database and infrastructure ---

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-migrate:
	$(ALEMBIC) upgrade head

db-revision:
	$(ALEMBIC) revision --autogenerate -m "$(msg)"

compose-check:
	docker compose config --quiet

infra-up:
	docker compose up -d postgres redis redpanda
	@echo "Waiting for local services..."
	@sleep 5
	docker compose run --build --rm migrate

infra-down:
	docker compose down

# --- Application ---

run:
	$(PYTHON) -m uvicorn confidence.api.app:app --reload --host 0.0.0.0 --port 8000

run-worker:
	$(PYTHON) -m confidence.workers.event_consumer

# --- Docker ---

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

# --- Cleanup ---

clean:
	find src tests alembic -type f -name "*.py[co]" -delete
	find src tests alembic -type d -name "__pycache__" -empty -delete
	rm -rf .hypothesis .mypy_cache .pytest_cache .ruff_cache htmlcov .coverage coverage.xml build dist
	find . -maxdepth 1 -type d -name "*.egg-info" -exec rm -rf {} +
