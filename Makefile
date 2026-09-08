.PHONY: install test lint format typecheck check db-up db-down db-migrate db-revision \
       clean docker-up docker-down venv infra-up infra-down run run-worker \
       test-unit test-integration test-adversarial test-load all-checks

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
ALEMBIC := $(VENV)/bin/alembic

venv:
	python3 -m venv $(VENV)
	$(PIP) install -e ".[dev]"

install:
	$(PIP) install -e ".[dev]"

# --- Testing ---

test:
	$(PYTEST) tests/ -v --tb=short --ignore=tests/load -q

test-unit:
	$(PYTEST) tests/test_engine.py tests/test_safety_contract.py tests/test_domain.py \
	          tests/test_actions.py tests/test_event_contracts.py tests/test_schema.py -v

test-adversarial:
	$(PYTEST) tests/test_adversarial.py tests/test_failure_injection.py \
	          tests/test_properties.py -v --tb=long

test-load:
	$(VENV)/bin/locust -f tests/load/locustfile.py --headless -u 50 -r 10 \
	          --run-time 30s --host http://localhost:8000

# --- Code Quality ---

lint:
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

format:
	$(RUFF) format src/ tests/

typecheck:
	$(MYPY) src/ --ignore-missing-imports

check: lint typecheck test

all-checks: lint typecheck test test-adversarial

# --- Database ---

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-migrate:
	$(ALEMBIC) upgrade head

db-revision:
	$(ALEMBIC) revision --autogenerate -m "$(msg)"

# --- Infrastructure ---

infra-up:
	docker compose up -d postgres redis redpanda
	@echo "Waiting for services to be healthy..."
	@sleep 5
	docker compose run --rm migrate

infra-down:
	docker compose down

# --- Application ---

run:
	$(PYTHON) -m uvicorn confidence.api.app:app --reload --host 0.0.0.0 --port 8000

run-worker:
	$(PYTHON) -m confidence.workers.event_consumer

# --- Docker ---

docker-up:
	docker compose up -d

docker-down:
	docker compose down

# --- Cleanup ---

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache build dist *.egg-info
