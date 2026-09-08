# Contributing to Confidence Layer

Thank you for improving Confidence Layer. This guide defines the shared development workflow and the checks required before code is merged.

## Before you start

1. Read the [README](README.md), [architecture overview](docs/architecture/overview.md), and [security controls](docs/safety/security-controls.md).
2. Create a focused issue for behavior changes, schema changes, or work that affects a safety invariant.
3. Keep synthetic demo behavior clearly separated from future operator integrations.

## Development setup

```bash
git clone https://github.com/Saisharathchandranandnetha/Confidence-layer.git
cd Confidence-layer
cp .env.example .env
make venv
.venv/bin/pre-commit install
make check
```

Use `make infra-up` when the change needs local PostgreSQL, Redis, or Redpanda. The default automated tests use isolated substitutes where possible.

## Branch and commit workflow

- Branch from an up-to-date `main`.
- Use a short branch name such as `feat/readiness-checks`, `fix/idempotency-scope`, or `docs/team-workflow`.
- Keep commits small enough to review and give each commit a clear, imperative subject.
- Do not mix broad formatting changes with behavior changes.
- Rebase or merge the latest `main` before requesting final review when the branch has drifted.

## Architecture boundaries

| Area | Responsibility | Dependency rule |
| --- | --- | --- |
| `domain/` | Models, safety contracts, action eligibility, deterministic policy | Must not import API or infrastructure code |
| `application/` | Use-case orchestration | Depends on domain contracts and injected ports |
| `api/` | HTTP schemas, routes, and dependency wiring | Translates transport data into application calls |
| `infrastructure/` | PostgreSQL, Redis, Kafka, authentication, resilience | Implements domain/application ports |
| `demo/` | Synthetic providers and scenarios | Must remain gated to local/test runtime |
| `workers/` | Background event processing | Must make retry, ordering, and commit behavior explicit |

Record durable architecture decisions in `docs/decisions/`. Update the README and documentation index when public commands, paths, configuration, or behavior change.

## Safety-sensitive changes

Changes to safety evaluation, policy eligibility, factual response generation, authentication, authorization, audit records, idempotency, or event recovery require extra care:

- State the invariant or failure mode being changed.
- Add tests for the safe path and the fail-closed path.
- Include evidence that `NO_INTERVENTION` remains available.
- Avoid conversion or uplift claims without measured, reviewable evidence.
- Request review from someone familiar with the affected safety or security boundary.

## Database migrations

- Add a new Alembic revision; do not rewrite a migration that may already have been applied.
- Provide both `upgrade()` and `downgrade()` behavior where reversal is safe.
- Keep SQLAlchemy metadata and migration state aligned.
- Verify generated SQL and, for material changes, test against PostgreSQL rather than SQLite alone.

## Code quality

Run the pull-request gate before pushing:

```bash
make check
make compose-check
```

`make check` runs Ruff linting and formatting checks, strict mypy checks, pytest, and the 75% branch-coverage regression floor. Use `make format` to apply safe automatic fixes. Load tests are separate because they require a running API:

```bash
make test-load
```

Tests should verify public behavior or a meaningful invariant. Avoid tests that only repeat implementation details. Name fixtures and scenarios for the condition they establish.

## Pull requests

Every pull request should contain:

- A concrete problem statement and resulting behavior.
- The affected boundary or module.
- Validation commands and results.
- Safety, security, schema, configuration, and deployment impact where applicable.
- Documentation updates for user-visible changes.

Normal changes require at least one approving review. Changes to a safety contract, authentication/authorization boundary, database schema, or deployment control should receive a second review from an owner of that area when the team has that capacity.

## Suggested ownership

Assign explicit people in the hosting platform as the team grows. Until then, use these review areas:

| Review area | Paths |
| --- | --- |
| Domain and safety | `src/confidence/domain/`, safety tests |
| API and application | `src/confidence/api/`, `src/confidence/application/` |
| Data and messaging | `src/confidence/db/`, `src/confidence/infrastructure/`, `alembic/` |
| Runtime and delivery | `Dockerfile`, `docker-compose.yml`, `k8s/`, `.github/workflows/` |
| Quality and documentation | `tests/`, `docs/`, repository tooling |

## Definition of done

A change is ready to merge when:

- The requested behavior is complete and covered at the right test level.
- `make check` passes.
- Relevant Compose, migration, or runtime checks pass.
- New configuration is documented in `.env.example` and the README.
- Security and safety failure modes are addressed.
- Generated files, secrets, debug output, and one-off repair scripts are absent.
- The pull request has the required review and no unresolved comments.

Use the private process in [SECURITY.md](SECURITY.md) for suspected vulnerabilities.
