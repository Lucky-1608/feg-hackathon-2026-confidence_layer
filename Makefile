.PHONY: install test lint format typecheck check db-up db-down db-migrate db-revision clean docker-up docker-down venv

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

test:
	$(PYTEST) tests/ -v

lint:
	$(RUFF) check src/ tests/

format:
	$(RUFF) format src/ tests/

typecheck:
	$(MYPY) src/

check: lint typecheck test

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-migrate:
	$(ALEMBIC) upgrade head

db-revision:
	$(ALEMBIC) revision --autogenerate -m "$(msg)"

clean:
	rm -rf __pycache__ .mypy_cache .ruff_cache .pytest_cache build dist *.egg-info

docker-up:
	docker compose up -d

docker-down:
	docker compose down -v
