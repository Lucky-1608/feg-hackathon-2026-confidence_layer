# Confidence Layer production audit — 2026-09-06

This audit covers local `main` at `a34d655`, including the working tree present at the start of the audit. It is an implementation assessment, not a production certification. The existing system should be hardened incrementally; its domain, decision engine, demo, and infrastructure adapters are substantial reusable work.

**Result:** the audit and first hardening increment are complete. Safety ordering, policy eligibility, audit snapshot fidelity, demo isolation, effective safety settings and local checks were improved. `make check` now passes with **161 tests**, lint, formatting and mypy. The component matrix records the starting state; the completed-change table below records the delta. Production readiness remains unproven.

## Scope and evidence

The user's project handoff is the governing request. The pitch deck and Phases 2–11 playbook are historical reference material. The deck's weighted harm objective, contextual bandit, latency and uplift claims are not implementation evidence. The playbook's assumption that no code exists is obsolete. Deterministic policy, hard safety constraints, safe abandonment, a static action registry, and no LLM financial or safety authority remain the design.

The user confirmed no operator contracts are available and instructed continued use of the existing interfaces. A deployment target has not been provided. No FEG-specific APIs or credentials have been invented.

Methods: graph vocabulary expansion and bounded traversal, direct source and call-site inspection, current tests/static analysis, isolated ASGI/engine probes, Compose configuration validation, and offline Alembic SQL generation. The existing graph was built at `ff2abd4`; source and runtime evidence take precedence over this older index. `docs/evaluation/implementation-audit.md` describes the initial empty repository and is not a current assessment.

There were 13 modified files before this work: `fix_ui_auth.py`; application `event_processor.py`; domain `ports.py`; infrastructure `dlq.py`, `event_ordering.py`, `resilience.py`, `session_state.py`; workers `__init__.py`, `event_consumer.py`; and four test files (`test_event_bus`, `test_policy`, `test_resilience`, `test_session_state`). Their edits were retained. A binary diff snapshot was saved to `/tmp/confidence-pre-audit.patch` before hardening.

Graph expansion used these exact existing vocabulary tokens: `decision safety auth redis kafka readiness metrics tracing persistence resilience worker policy`. The code graph was refreshed after changes (1,171 nodes / 2,091 edges); semantic documentation extraction was not rebuilt. Component paths abbreviated as `domain/...`, `application/...`, `api/...` or `infrastructure/...` refer to `src/confidence/`.

### Baseline checks

| Check | Observed result | What this establishes |
|---|---|---|
| `.venv/bin/pytest tests/ --ignore=tests/load -q --tb=short` | 121 passed, 4 Redis-close deprecation warnings | Current unit/synthetic scenarios pass; not real dependency integration |
| `.venv/bin/ruff check src/ tests/ --output-format concise` | 54 findings | Earlier clean-lint claim does not hold for the starting tree |
| `.venv/bin/ruff format --check src/ tests/` | 12 files need formatting | Starting format check fails |
| `.venv/bin/mypy src/ --ignore-missing-imports` | One error: float assigned into inferred integer updates in `event_processor.py` | Starting type check fails |
| `docker compose config --quiet` | Passed | Compose syntax/interpolation only |
| `.venv/bin/alembic upgrade head --sql` | Both migrations generate PostgreSQL SQL | Does not execute migrations against PostgreSQL |
| `docker compose ps --all` | Docker socket permission denied, including outside sandbox | Container availability and images cannot be verified here |
| Local interpreter | Python 3.14.7 | Docker/CI declare 3.12; local evidence is not a 3.12 run |

No production traffic, operator integration, live database/broker outage test, browser end-to-end run, load result, penetration test, or backup restoration was observed. Tests named “integration”, “failure injection”, “adversarial”, or “properties” are evaluated by their assertions, not their filenames.

## Component inventory at audit baseline

Statuses: **IMPLEMENTED** means the scoped behavior exists with direct evidence, not that it is certified for production. **PARTIAL** means real code exists but essential integration/validation is incomplete. **DEMO-FAKE** means a deliberate stub/synthetic implementation. **BROKEN** means a demonstrated failure or a direct contradiction in an active path. **MISSING** means no implementation was found. P0 blocks exposure to real users; P1 blocks a defensible production pilot; P2 is subsequent hardening. These are engineering priorities, not legal determinations.

| Component | Status | Evidence | Actual gap / next acceptance condition | Priority |
|---|---|---|---|---|
| Domain models and contracts | IMPLEMENTED | `domain/models.py`, `enums.py`; domain/schema tests | Models exist; docs overstate strict validation. Numeric ranges, finite values, timezone and freshness contracts need tightening | P1 |
| Safety Authority | PARTIAL | `domain/safety.py`; extensive S1–S17 scenario tests | Blocks known unsafe/unknown/stale data; permits future timestamps and freshness-only safety records with default false flags. Authoritative completeness needs an explicit contract | P0 |
| Safety ordering in engine | BROKEN | `application/engine.py:_execute_pipeline` | Policy is called before safety/confidence/reconsideration overrides. Unsafe candidate sets can contain factual actions | P0 |
| State Authority | IMPLEMENTED | `domain/state.py`; A–H scenarios | Deterministic rules exist. Confidence values are fixed heuristic scores; no calibration/empirical classification-quality evidence | P1 |
| Static action registry | PARTIAL | `domain/actions.py` | Six registered actions; no `SHOW_RULES_REFERENCE`. Policy result is not checked against eligible IDs; NO_INTERVENTION presence is checked but a custom definition can disable it | P0 |
| Deterministic policy | PARTIAL | `domain/policy.py`; policy tests | Default path is deterministic. Engine must enforce eligible membership even for a faulty replacement policy | P0 |
| Decision timeout/fail closed | PARTIAL | `engine.decide`, timeout scenario | Async pipeline timeout works. Redis lookups/writes and dependency construction are outside it; synchronous work can overrun cooperative timeout | P1 |
| Authoritative context adapters | DEMO-FAKE | `api/dependencies.py:get_context_builder`, `demo/providers.py` | Always uses dummy safety/slip/market providers; actor/slip IDs select demo scenarios. No environment guard or real provider selection at baseline | P0 |
| Provider interfaces | IMPLEMENTED | `domain/ports.py` | Safety, slip, market and persistence protocols exist; retain them while waiting for operator contracts | P1 |
| Factual response generation | PARTIAL | `domain/response.py`, `_compute_available_data_keys` | No LLM/calculation authority. Eligibility uses first market, generation matches first selection; unmatched market can produce an empty definition. No market-freshness gate; multi-selection and odds-history semantics need validation | P0 |
| API decisions/events | PARTIAL | `api/routes.py`, `api/models.py` | Real routes; only health is covered by baseline API test. No ownership authorization; operational errors can bypass engine fallback | P0 |
| PostgreSQL/schema/migrations | PARTIAL | `db/schema.py`, `alembic/versions/001*`, `002*`, SQLite schema tests | Ten-table foundation exists. No real PostgreSQL test; migration 002 duplicates session index under another name absent from metadata | P1 |
| Decision persistence | PARTIAL | `infrastructure/persistence.py` | Real transaction/upsert path, but broad SQL fallback attempts SQLite syntax on any PostgreSQL error and swallows failures. Needs dialect-specific behavior and real write tests | P1 |
| Audit truthfulness | BROKEN | `engine._schedule_persistence` | Rebuilds empty slip/default safety context after the decision instead of preserving facts used | P0 |
| Audit durability/lifecycle | PARTIAL | engine background tasks; `infrastructure/audit.py` | Tasks are untracked/unbounded and not drained at shutdown; no durable queue/outbox, reconciliation or audited loss policy. Kafka audit implementation is not wired into API | P0 |
| Redis session store | PARTIAL | `session_state.py`, fakeredis tests | WATCH/MULTI updates exist. Validation occurs after writing; retry loop unbounded. Decision context reads request telemetry, not Redis state | P1 |
| Kafka/Redpanda publishing | PARTIAL | `event_bus.py`, API lifespan | Actual producer and session partition keys exist. Baseline test only uses in-memory publisher; broker durability, timeouts, readiness, TLS/auth and restart behavior unvalidated | P1 |
| Event consumer | BROKEN | `workers/event_consumer.py` | A failed record can be skipped by a later offset commit; withholding the failed commit does not seek/retry it. No sequence check or event dedupe on active path | P0 |
| Event ordering | PARTIAL | `event_ordering.py`, fakeredis test | Atomic sequence Lua exists but has no production caller. State mutation and sequence advancement are separate operations | P1 |
| Event contracts | PARTIAL | `event_contracts.py`, tests | Envelope validates IDs/nonnegative sequences. Schema version is arbitrary, payload/context unbounded dictionaries; payload type and privacy enforcement missing | P1 |
| API idempotency | PARTIAL | `routes.py`, `RedisIdempotencyStore` | SET NX/cache works for simple tests; no caller/session/body binding, failed locks remain for an hour, Redis clients created per request without close. Same key can return another request's result | P0 |
| Dead letter queue | BROKEN | `dlq.py`, worker exception paths | Real Kafka producer exists, but `push` swallows delivery errors; worker commits invalid records even when DLQ delivery failed | P0 |
| Authentication | DEMO-FAKE | `infrastructure/auth.py` | Only literal `demo-token` accepted; returns constant `user-123`. No JWT signature/issuer/audience/expiry validation | P0 |
| Authorization / identity binding | MISSING | `user_id` unused in both mutation routes | Bind subject/operator to session, actor and slip before fetching authoritative facts or using cached results | P0 |
| Rate limiting / backpressure | MISSING | `.env.example`; unused `ConcurrencyLimiter` | No rate enforcement/callers. Configuration lines are not parsed into active controls | P1 |
| Circuit breakers / retry isolation | PARTIAL | `resilience.py`, `ContextBuilder.build` | Breaker unit implementation exists; each provider call constructs a fresh config/breaker, so failures never accumulate across calls. Half-open allows concurrent probes; retries have no backoff | P1 |
| Prometheus | PARTIAL | `observability/metrics.py`, route increments | Three instruments exist; `/metrics` is 404. Missing decision/safety/audit/worker counters, useful sub-100ms buckets and alerts | P1 |
| OpenTelemetry | PARTIAL | `observability/tracing.py` | Console setup is never called; no active spans/instrumentation/exporter/propagation/resource identity/shutdown. Installed packages alone do not trace requests | P1 |
| Structured logs / correlation | PARTIAL | `log.py`, call sites | JSON logging exists; no request-wide bound correlation IDs, redaction policy, or trace linkage. Exceptions and raw messages may contain sensitive inputs | P1 |
| Liveness | IMPLEMENTED | `/health` API test | Process liveness works; duplicate registration should be removed | P2 |
| Readiness | BROKEN | both `app.py` and `routes.py` | Active route reports unconfigured DB as ready, probes no Redis/Kafka, has no bounded check timeout and returns raw exception text; router copy always succeeds | P1 |
| Environment/configuration | BROKEN | `config.py`, env examples | `APP_ENV`, `DEMO_MODE`, `AUTH_PROVIDER`, `STATE_CONFIDENCE_THRESHOLD` do not control their advertised behavior. Nested settings instantiated at import; SafetyContract ignores configured values | P0 |
| Demo UI | IMPLEMENTED | `ui/index.html`, `app.js` | Real API integration and safe dismissal; response JSON is presented as “audit”, not durable full audit. No outcome delivery, HTTP-status handling or browser regression evidence; stake edits don't update synthetic authoritative stake | P1 |
| Market service failure demo | MISSING | `DummyMarketProvider`, UI slip IDs | Provider always succeeds; do not claim this scenario is demonstrated | P2 |
| Outcome ingestion and persistence | MISSING | Outcome model/table only; no route | Needed for resolved/declined/deferred outcomes and decision-quality evaluation | P1 |
| Evaluation / experiments | MISSING | `evaluation/__init__.py` is a docstring; experiment schema only | No offline datasets, classification metrics, harm guardrail analysis, counterfactual/controlled experiment implementation, or evidence of uplift | P1 |
| Replay | DEMO-FAKE | `application/replay.py` | Toggles a boolean; does not read/seek/process records | P2 |
| Model registry | DEMO-FAKE | `MLflowRegistryAdapter` | Returns fixed version/dummy weights; not wired. Not needed for deterministic V1; don't build prematurely | P2 |
| Real dependency integration tests | MISSING | tests use SQLite/fakeredis/in-memory publisher | Need disposable PostgreSQL, Redis and Redpanda with persistence, delivery, duplicate, restart and failure assertions | P1 |
| Adversarial/property/failure evidence | PARTIAL | engine safety scenarios; small dedicated test files | Useful engine coverage exists. Dedicated adversarial test accepts a number; property test only checks mapping is non-null; failure injection calls one dummy provider | P1 |
| Load/performance/SLOs | PARTIAL | `tests/load/locustfile.py`, `make test-load` | Load script exists with static session ID, no latency thresholds/result validation/artifacts; no p95/p99 or sustainable-capacity measurements | P1 |
| CI | BROKEN | `.github/workflows/ci.yml`, `Makefile` | CI installs globally then runs Make commands hard-coded to `.venv/bin`; clean runner won't have that venv. No dependency services or deployment job | P1 |
| Docker/Compose | PARTIAL | Dockerfile and valid Compose configuration | Non-root image and migration service exist; app lacks broker health dependency; no consumer service, Redis persistence, broker volume, reproducible image pinning, or image build evidence | P1 |
| Kubernetes / deployment | PARTIAL | `k8s/deployment.yaml` | Basic deployment/probes/secret reference only. No observed deploy, service/ingress, resource budgets, security context, network policy, rollout/capacity evidence | P1 |
| Secrets / dependency security / privacy | PARTIAL | local example credentials, `.gitignore`, `docs/safety/security-controls.md` | Security document describes controls not enforced in code. No dependency lock/SBOM/security scan; open dev service ports; no retention/deletion/TLS/redaction enforcement. Opaque field names do not guarantee zero PII | P0 |
| Runbooks / rollback / DR | MISSING | repository file inventory | No executable incident/rollback/restore procedures or backup/restore evidence | P1 |
| Global kill switch / shadow delivery | MISSING | active API/engine/UI call sites | No operational override or shadow-only output gate; required before a controlled pilot | P1 |

## Reproduced findings

1. **Policy can escape eligibility.** An injected policy returns `EXPLAIN_ODDS_CHANGE` for `NO_UNCERTAINTY` with the default providers. The engine responds with the factual action while `candidate_actions == [NO_INTERVENTION]`. Registration and fact availability alone do not establish eligibility. The default policy does not deliberately do this; the missing enforcement boundary makes a future policy defect unsafe.
2. **Audit snapshot contradicts the executed decision.** The same engine probe captures a persisted context with zero selections and `safety.data_freshness == None`, although the response explains valid odds using a populated slip and fresh safety state.
3. **False readiness.** An isolated ASGI request to `/ready` with no cached engine returns HTTP 200 and `{"status":"ready","checks":{"database":"not_configured"}}`.
4. **Metrics not exposed.** Isolated ASGI `/metrics` returns HTTP 404.
5. **CI path mismatch.** Workflow global `pip install` does not create the `.venv/bin/ruff`, `.venv/bin/mypy` and `.venv/bin/pytest` used by `make check`. This is source evidence; the hosted workflow was not run.

## First hardening increment

Baseline classifications above are retained so remaining gaps cannot be mistaken for resolved ones.

| Completed change | Evidence after hardening | Remaining limit |
|---|---|---|
| Hard gates precede policy | `engine.py` bypasses policy for unsafe/unknown/stale safety, low confidence, reconsideration and no uncertainty. Tests assert policy is never called and only NO_INTERVENTION appears as a candidate | Safety input completeness/freshness contract still requires operator definition; final check is not a new operator fetch |
| Eligible action enforcement | Faulty policy returning registered EXPLAIN_MARKET during ODDS_CHANGE now yields NO_INTERVENTION; baseline escape scenario is covered by abstention tests | Registry definitions still mutable; no untrusted-code isolation is claimed |
| Accurate audit snapshots | Deep copies preserve actual slip, market and safety facts and resist later request/result mutation. Failed context construction is explicitly marked `context_version=unavailable` | Async persistence remains best effort, unbounded and undrained; incomplete/failed pipelines may lack full context |
| Useful failure responses | Abstention reason is returned in existing `reason`; internal pipeline exception text is no longer returned to the client | Logging redaction and richer structured API reason fields remain gaps |
| Demo isolation and configuration | Production/staging/unknown environment, disabled demo mode or non-development auth refuses startup before Kafka and cannot obtain dummy providers/demo authentication. Nested settings load dynamically from environment/dotenv; safety freshness and confidence thresholds are wired and bounded | Real JWT/ownership/operator adapters are not implemented. Local defaults intentionally remain demo; deployment must explicitly configure its environment |
| Static-check repairs | Preserved pre-existing application edits; corrected update typing, imports, generic syntax and whitespace in source/tests/migrations; updated FakeRedis cleanup to `aclose()` | No lint, formatting, type-check, test, or diff-whitespace findings remain in the local gate |
| CI virtual environment | Workflow creates `.venv`, installs development dependencies, uses read-only permissions, cancels superseded runs, and executes `make check` | Hosted GitHub workflow and Python 3.12 execution have not been observed |
| API/demo regressions | Nine API scenarios exercise bearer dependency, request validation, engine wiring, response and static UI delivery with storage stubbed | No real Kafka/Redis/PostgreSQL or browser interaction evidence from these tests |
| Repository and documentation hygiene | Root repair/scratch scripts were removed; docs were categorized; README, contributor/security policies, templates, editor settings, pre-commit hooks, and dependency update configuration were added | Historical plan/audit documents remain clearly labeled historical artifacts |

Final verification: **`make check` exited 0** — Ruff lint and formatting passed across 67 source, test, and migration files; mypy passed on 43 source files; and **161 tests passed without warnings in 2.81 seconds**, using Python 3.14.7. Branch-aware coverage was **77.83%**, above the enforced 75% regression floor. The sandboxed API test run stalled at the FastAPI worker-thread boundary; the complete check ran successfully outside the sandbox. Compose configuration, Markdown links, YAML syntax, pre-commit configuration, `git diff --check`, and wheel construction also passed. The built wheel contains the application and static UI assets. No source changes were committed, pushed, or deployed.

This increment does not establish durable auditing, production authentication, valid operator data, event delivery guarantees, or readiness. Those remain release blockers even if the targeted tests pass.

## Next increments and acceptance evidence

1. **Authoritative inputs and access boundary (P0).** Once FEG contracts exist, implement only the existing required ports; define safety completeness/freshness and fact versioning, actor/session/slip ownership, signed identity validation and cached-response scope. Show exclusion/restriction and dependency-failure cases through real API auth and provider adapters. Keep production startup closed until these are configured.
2. **Audit and delivery correctness (P0).** Define a durable handoff within the latency budget, including an explicit loss/overflow policy. Verify exact decision facts, failure records, shutdown drain and reconciliation. Process records with explicit partition offsets; retry/seek or halt on transient failure, acknowledge DLQ only after broker confirmation, and couple dedupe/ordering to state updates. Prove crash/restart behavior against real dependencies.
3. **API/runtime reliability (P1).** Shared managed Redis clients, bounded readiness across required dependencies, end-to-end deadline, persistent circuit breakers, rate limits and overload behavior. Add integration services/worker wiring to CI and local Compose. Prove startup/unavailable/recovery behavior with bounded responses.
4. **Observable operations (P1).** Expose metrics, instrument/export traces, bind correlation IDs and redact inputs, then supply dashboards, alerts, capacity/SLO assumptions, deploy/rollback procedures and tested backups. Use measured p95/p99 at declared arrival rates; include NO_INTERVENTION rate and audit/delivery failures so fast errors cannot masquerade as throughput.
5. **Research/evaluation (P1).** Record accepted, declined and deferred resolutions; curate labeled uncertainty cases and legitimate-reconsideration controls; evaluate calibration and abstention, usefulness, avoidable abandonment, harm indicators and preserved abandonment. Predefine experiment metrics/margins with operator input; simulated or unit-test results cannot establish causal uplift or harm neutrality. RAG, LLMs and adaptive policy are not prerequisites.

Production readiness requires evidence across these increments and the eventual target environment. The defensible present description is **a deterministic safety-aware decision system with real infrastructure foundations and unresolved production boundaries**.
