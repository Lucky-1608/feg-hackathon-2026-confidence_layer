# Confidence Layer

**Decision support for betslip uncertainty — FEG Innovation Hackathon 2026**

Confidence Layer detects user uncertainty during betslip confirmation and provides contextually appropriate interventions — or deliberately chooses not to intervene — while structurally enforcing safety constraints.

> **Note:** This is a hackathon prototype. All data is synthetic and explicitly labeled as such. No real-world validation or customer uplift claims are made.

## Core Hypothesis

When a user hesitates during betslip confirmation, the system can distinguish between different types of uncertainty (information gaps, legitimate reconsideration, potential harm) and provide appropriate responses without compromising safety.

## Architecture

```
Safety Authority → Eligibility Filter → Policy Authority → Response
     ↑                    ↑
State Authority ──────────┘
```

Three independent authorities:
- **Safety Authority**: "Can we intervene?" (fail-closed, never optimizes conversion)
- **State Authority**: "What is happening?" (classifies uncertainty type)
- **Policy Authority**: "Which safe action?" (selects from pre-approved actions only)

Safety is a **hard gate**, not a penalty term. The optimizer never sees unsafe actions.

## Quick Start

```bash
# Prerequisites: Python 3.12+, Docker, Docker Compose

# Clone and install
git clone <repo-url>
cd Confidence
pip install -e ".[dev]"

# Start PostgreSQL
make db-up

# Run migrations
make db-migrate

# Run tests
make test

# Run all checks (lint + typecheck + test)
make check
```

## Development

```bash
make install     # Install with dev dependencies
make test        # Run tests
make lint        # Run ruff linter
make format      # Auto-format code
make typecheck   # Run mypy strict type checking
make check       # Run lint + typecheck + test
make clean       # Clean build artifacts
```

## Docker

```bash
make docker-up   # Start all services
make docker-down # Stop and clean up
```

## Project Structure

```
src/confidence/
├── domain/          # Strongly typed domain models
│   ├── enums.py     # All enumerations
│   ├── models.py    # Pydantic domain objects
│   ├── events.py    # Versioned event schema
│   ├── actions.py   # Action registry
│   └── safety.py    # Safety contract (S1-S17)
├── db/              # Database layer (persistence/audit)
│   ├── schema.py    # SQLAlchemy table definitions
│   └── connection.py
├── config.py        # Environment-based configuration
└── log.py           # Structured logging
```

## Safety Invariants

The system enforces 17 safety invariants (S1-S17). Key examples:
- Self-excluded users receive NO_INTERVENTION
- Harmful-play states block conversion-oriented actions
- Unknown safety state → fail closed
- Model confidence below threshold → NO_INTERVENTION
- All failures → NO_INTERVENTION

See [Safety Contract](src/confidence/domain/safety.py) for the full list.

## Documentation

- [Implementation Audit](docs/IMPLEMENTATION_AUDIT.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [ADR-001: Architecture](docs/ADR-001-ARCHITECTURE.md)
