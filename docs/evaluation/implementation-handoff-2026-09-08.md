# Implementation handoff — 2026-09-08

The eight requested implementation phases are present. This records code and automated-test evidence, not certification for operator deployment. It supersedes feature-status claims in the September 6 audit; that audit remains a historical record.

## Delivered

| Phase | Implementation |
| --- | --- |
| 1: Foundation | Redis interaction merge and shared clients, sequence-aware event retries and DLQ delivery, persistent circuit breakers, bounded dependency readiness |
| 2: Outcomes | Authenticated outcome ingestion, decision joins, durable outcome/reward outbox and retry-safe outcome IDs |
| 3: SQS | Versioned scoring and persistence, aggregate API, startup weight validation, positive terms suppressed when harm is observed |
| 4: ML | Bounded LightGBM and Vowpal Wabbit adapters with deterministic fallback, evaluation-gated training/registry, trainer recovery from model/offset checkpoints |
| 5: Harm | Independent cross-session feature schema and sensitive classifier, backwards-compatible indicators, history port that marks missing financial facts incomplete |
| 6: Controls | JWT/JWKS validation, identity/session ownership, Redis rate limits, global kill switch, auditable shadow decisions |
| 7: Operations | Authenticated Prometheus metrics, optional OTLP tracing, request IDs, background audit draining, isolated historical replay |
| 8: Evaluation | Classifier/SQS/harm analysis, deterministic experiment assignment, permanent 5% holdout, daily report generation |

Safety gates precede candidate filtering and policy selection. The action registry and controlled response templates remain the source of available interventions and factual response text. The kill switch is checked before waiting for decision concurrency capacity, within the decision timeout. Audit persistence runs asynchronously.

## API access

| Endpoint | Required scope |
| --- | --- |
| `POST /v1/decisions` | `decisions:write` |
| `POST /v1/events` | `events:write` |
| `POST /v1/outcomes` | `outcomes:write` |
| `GET /v1/metrics/sqs?window=24h` | `metrics:read` |
| `GET /metrics/` | `metrics:read` |
| `POST /v1/admin/kill-switch` | `admin:global` |

JWTs require RS256 signatures, issuer, audience, expiry, subject and `operator_id`; scopes come from the space-separated `scope` claim. Decision/event actor IDs must match the token subject, and Redis binds sessions to the operator/subject identity. The development token has no global admin scope. Health, readiness, documentation and demo UI remain public.

## Models and workers

Defaults use the rule estimator and deterministic policy. `.env.example` documents optional model paths and runtime controls. Training requires labeled JSONL records containing `context` and `label`, with disjoint actor sets between training and validation:

```bash
.venv/bin/python -m confidence.ml.train_hesitation TRAIN.jsonl VALIDATION.jsonl OUTPUT.lgb
.venv/bin/python -m confidence.workers.event_consumer
.venv/bin/python -m confidence.workers.bandit_trainer
```

These are separate processes. The trainer consumes `confidence.rewards` and checkpoints under the file model registry; checkpointing does not establish that a model is suitable for promotion. No production model quality or harm-neutrality result is claimed without evaluation data.

## Verification

- `make check`: Ruff lint and format passed; mypy passed for 69 source files; 227 tests passed; branch-aware coverage was 83.83% against the 75% floor.
- `make compose-check`: passed.
- Automated checks include a complete SQLite migration upgrade/downgrade and offline PostgreSQL upgrade SQL, authenticated metrics, isolated application lifecycle, real LightGBM artifact loading and Vowpal Wabbit checkpoint recovery, plus failure and safety regression cases.
- The check ran outside the filesystem/process sandbox after the sandboxed test run stalled. Tests use SQLite, fake Redis and mocked broker behavior; they do not establish live PostgreSQL/Redis/Kafka recovery or production latency.

## Remaining deployment work

Provide real operator safety/slip/market adapters and settlement/deposit feeds. Built-in production authority placeholders fail closed, and stored session history explicitly lacks authoritative financial totals. Supply independent labeled datasets and reviewed model artifacts before enabling learned inference.

Validate upgrades on PostgreSQL, broker outages and replay, sustained load, and multi-process recovery in a representative environment. Asynchronous audit writes can still be lost on abrupt process termination; shutdown draining is not a durable audit queue. The outcome outbox protects outcome/reward publication, not every decision audit.

Configure service credentials/TLS, network access, CORS, retention and deployment monitoring. Existing local Compose and Kubernetes files are deployment foundations. Migrations 001/002 were edited in the recovered work; compare already-applied schemas and prepare a forward migration if an older database exists before rolling out this revision.
