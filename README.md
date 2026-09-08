# Confidence Layer

### Safety-constrained decision support for high-intent betslip moments

**FEG Innovation Hackathon 2026 — Challenge 1**

Confidence Layer is a decision-support prototype designed to detect **resolvable uncertainty during betslip confirmation** and provide an appropriate factual clarification — or deliberately choose **`NO_INTERVENTION`** when intervention is unsafe, unnecessary, unsupported, or uncertain.

The core design principle is simple:

> **Do not optimize for conversion first. Determine whether intervention is safe, determine what is actually happening, and only then select an appropriate action.**

---

## ⚠️ Prototype Status

> **This is a synthetic hackathon prototype.**
>
> * All demonstration data is synthetic.
> * No real customer data is used.
> * No real-world uplift or business-impact claim is made.
> * No production gambling operator integration is included.
> * The system is not intended to make gambling decisions for users.
> * Safety constraints take precedence over intervention or conversion objectives.

Current implementation:

| Phase                                     | Status                       |
| ----------------------------------------- | ---------------------------- |
| Phase 1 — Domain & Safety Foundation      | ✅ Complete                   |
| Phase 2 — Deterministic Decision Engine   | ✅ Complete                   |
| Phase 3 — Interactive Demonstration Layer | ✅ Complete                   |
| Phase 4 — Evaluation Framework            | 🔜 Next                      |
| Production Deployment                     | ❌ Out of scope for prototype |

---

# 1. The Problem

A user can spend significant time configuring a betslip and still stop at the final confirmation step.

That hesitation can have very different causes.

For example:

* The user may not understand what a market means.
* The odds may have changed.
* The betslip may no longer contain the selections the user intended.
* The user may simply be reconsidering the bet.
* The user may be exhibiting potentially harmful-play behavior.
* An authoritative dependency may be unavailable.
* There may be insufficient evidence to determine what is happening.

These situations should **not** receive the same response.

A system that blindly attempts to reduce abandonment can create unsafe behavior.

Confidence Layer therefore treats abandonment as potentially legitimate and asks a different question:

> **Is there a safe, evidence-backed information gap that can be resolved without pressuring the user?**

If the answer is no, the correct decision can be:

```text
NO_INTERVENTION
```

---

# 2. Core Hypothesis

When a user hesitates during betslip confirmation, the system can distinguish between:

```text
Information uncertainty
        ↓
Legitimate reconsideration
        ↓
Potential harm
        ↓
No meaningful uncertainty
```

and respond accordingly.

The system does **not** assume:

```text
Abandonment = problem
```

Instead:

```text
Abandonment
    ↓
Understand context
    ↓
Check safety
    ↓
Classify state
    ↓
Determine whether intervention is justified
    ↓
Select only an approved action
    ↓
Otherwise → NO_INTERVENTION
```

---

# 3. Design Philosophy

Confidence Layer is built around three independent authorities.

## Safety Authority

Answers:

> **"Can we intervene?"**

Safety is a hard constraint.

The system must never optimize through unsafe states.

---

## State Authority

Answers:

> **"What is happening?"**

The state estimator classifies the current interaction context.

Examples:

```text
ODDS_CHANGE
MARKET_MEANING
SLIP_CONFIGURATION
STAKE_RETURN
LEGITIMATE_RECONSIDERATION
POTENTIAL_HARM
NO_UNCERTAINTY
UNKNOWN
```

---

## Policy Authority

Answers:

> **"Which safe action, if any?"**

The policy layer can only choose from the approved Action Registry.

It cannot invent arbitrary interventions.

---

# 4. System Architecture

```text
                    ┌─────────────────────────┐
                    │   Client / Betslip UI    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Decision API        │
                    │     POST /v1/decisions   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Context Builder      │
                    │                           │
                    │ Safety + Slip + Market   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     SAFETY AUTHORITY     │
                    │                           │
                    │ Can we intervene?        │
                    └────────────┬────────────┘
                                 │
                     ┌───────────┴───────────┐
                     │                       │
                  BLOCKED                  SAFE
                     │                       │
                     ▼                       ▼
              NO_INTERVENTION       ┌─────────────────┐
                                     │ STATE AUTHORITY │
                                     │                 │
                                     │ What is        │
                                     │ happening?     │
                                     └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │ ACTION ELIGIB.  │
                                     └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │ POLICY AUTHORITY│
                                     │                 │
                                     │ Which action?   │
                                     └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │ FINAL SAFETY    │
                                     │ CHECK           │
                                     └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │ RESPONSE        │
                                     │ GENERATOR       │
                                     └────────┬────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │ DECISION + AUDIT│
                                     └─────────────────┘
```

---

# 5. Decision Flow

Every decision follows the same conceptual sequence:

```text
1. Receive request
2. Build authoritative context
3. Evaluate safety
4. Fail closed if safety is unknown/unavailable
5. Estimate interaction state
6. Determine eligible actions
7. Select policy-approved action
8. Run final safety check
9. Generate deterministic response
10. Record decision/audit information
11. Return result
```

The important property is:

> **Optimization never happens before safety.**

---

# 6. Safety Model

Safety is implemented as a **hard gate**, not as a negative term in an optimization score.

This distinction is fundamental.

A design such as:

```text
utility = conversion_value - harm_penalty
```

can still theoretically choose a harmful action if the conversion value is sufficiently large.

Confidence Layer instead uses:

```text
if unsafe:
    NO_INTERVENTION

if safety_unknown:
    NO_INTERVENTION

if dependency_failed:
    NO_INTERVENTION

otherwise:
    continue
```

---

## Safety Invariants

The system enforces safety invariants including:

### S1 — Self-exclusion

Self-excluded users cannot receive conversion-oriented interventions.

```text
SELF_EXCLUDED
      ↓
NO_INTERVENTION
```

### S2 — Protective restrictions

Protective restrictions block intervention where required.

### S3 — Harmful-play state

Strong harmful-play indicators prevent conversion-oriented intervention.

### S4 — Unknown safety

Unknown safety state fails closed.

### S5 — Safety dependency failure

If the authoritative safety dependency fails:

```text
NO_INTERVENTION
```

### S6 — Stale safety information

Stale safety information does not silently become trusted safety information.

### S7 — Low-confidence state

Insufficient confidence in the state estimate results in:

```text
NO_INTERVENTION
```

### S8 — Legitimate reconsideration

A user changing their mind is not automatically treated as a problem to overcome.

### S9 — Final safety check

Even after policy selection, the selected action passes through a final safety gate.

---

# 7. Action Registry

The system uses a finite registry of approved actions.

Current conceptual actions include:

```text
NO_INTERVENTION
EXPLAIN_MARKET
EXPLAIN_ODDS_CHANGE
VERIFY_SELECTIONS
SHOW_STAKE_RETURN
OFFER_DEFER
SHOW_RULES_REFERENCE
```

The registry prevents the policy layer from inventing arbitrary behavior.

For example:

```text
State:
    ODDS_CHANGE

Eligible:
    EXPLAIN_ODDS_CHANGE
    NO_INTERVENTION

Selected:
    EXPLAIN_ODDS_CHANGE
```

Whereas:

```text
State:
    POTENTIAL_HARM

Eligible:
    NO_INTERVENTION

Selected:
    NO_INTERVENTION
```

---

# 8. `NO_INTERVENTION` Is a First-Class Outcome

`NO_INTERVENTION` is not an error.

It is a legitimate and often correct system decision.

Possible reasons include:

```text
SELF_EXCLUDED
PROTECTIVE_RESTRICTION
POTENTIAL_HARM
UNKNOWN_SAFETY
STALE_SAFETY_DATA
SAFETY_DEPENDENCY_FAILURE
MISSING_AUTHORITATIVE_DATA
LOW_STATE_CONFIDENCE
LEGITIMATE_RECONSIDERATION
NO_RESOLVABLE_UNCERTAINTY
POLICY_BLOCKED
FINAL_SAFETY_CHECK_FAILED
TIMEOUT
```

This is one of the most important properties of the architecture.

The system must be capable of saying:

> **"Do nothing."**

---

# 9. Demonstration UI

Phase 3 adds an interactive browser-based demonstration layer directly to the FastAPI application.

No Node.js application or Webpack build is required.

The UI is served by the backend.

## Open the Demo

After starting the application:

```text
http://localhost:8000/
```

The root endpoint redirects to:

```text
http://localhost:8000/ui/
```

The current application mounts the static UI under `/ui`.

---

# 10. Demonstration Dashboard

The demonstration contains three primary panels.

## Panel 1 — Betslip

The mock betslip represents the user interaction surface.

It tracks mutable client-side telemetry such as:

```text
Dwell Time
Backtracks
Stake Changes
Odds Changed
```

The user can simulate interaction with the betslip.

---

## Panel 2 — Scenario Controls

The scenario controller allows the team to demonstrate authoritative conditions.

### Client signals

```text
Trigger Odds Change
User changed mind / Backtrack
```

### Safety states

```text
Normal User
Harmful Play / Loss Chasing
Self-Excluded
Safety Service Down
```

### Market states

```text
Normal Slip
Missing Odds History
Market Service Down
```

These controls are intentionally deterministic so the same scenario can be reproduced during a live hackathon demonstration.

---

## Panel 3 — Decision Pipeline

The pipeline visualizes:

```text
1. Safety Authority
        ↓
2. State Authority
        ↓
3. Policy Selector + Final Check
```

The UI displays:

* safety status
* detected state
* confidence
* selected action
* decision reason
* response text
* returned decision information

It also exposes the resulting JSON record for demonstration and debugging.

---

# 11. Demo Scenarios

The following scenarios should be used during the hackathon presentation.

## Scenario A — Odds Changed

### Setup

```text
Safety: Normal
Market: Normal
Client: Trigger Odds Change
```

### Expected behavior

The system detects an odds-change information state.

Expected action:

```text
EXPLAIN_ODDS_CHANGE
```

The user receives factual clarification rather than pressure.

---

## Scenario B — User Changed Their Mind

### Setup

```text
Safety: Normal
Market: Normal
Client: Backtrack
```

### Expected behavior

The system recognizes legitimate reconsideration.

Expected result:

```text
NO_INTERVENTION
```

The system does not attempt to convince the user to continue.

---

## Scenario C — Harmful Play

### Setup

```text
Safety: Harmful Play
```

### Expected behavior

Safety blocks conversion-oriented intervention.

Expected result:

```text
NO_INTERVENTION
```

---

## Scenario D — Self-Excluded

### Setup

```text
Safety: Self-Excluded
```

### Expected behavior

The safety authority blocks intervention.

Expected result:

```text
NO_INTERVENTION
```

---

## Scenario E — Safety Service Failure

### Setup

```text
Safety: Safety Service Down
```

### Expected behavior

The system fails closed.

Expected result:

```text
NO_INTERVENTION
```

---

## Scenario F — Missing Odds History

### Setup

```text
Market: Missing Odds History
```

### Expected behavior

The system cannot safely explain an odds movement without authoritative historical information.

Expected result:

```text
NO_INTERVENTION
```

---

## Scenario G — Market Service Failure

### Setup

```text
Market: Market Service Down
```

### Expected behavior

The system does not fabricate market information.

Expected result:

```text
NO_INTERVENTION
```

---

# 12. Mock Providers

The demonstration uses deterministic mock providers rather than real operator services.

Current providers include:

```text
DummySafetyProvider
DummySlipProvider
DummyMarketProvider
```

The demo uses special synthetic actor/slip identifiers to reproduce controlled conditions.

Examples:

```text
actor-normal
actor-harm
actor-self-excluded
actor-safety-down

slip-normal
slip-missing-odds
slip-down
```

These values are **demo controls**, not production integration mechanisms.

The provider interfaces are intentionally separated from the decision engine so that real authoritative services can replace the dummy implementations later.

---

# 13. API

## Health Check

```http
GET /health
```

Example:

```json
{
  "status": "ok"
}
```

---

## Readiness

```http
GET /ready
```

Example:

```json
{
  "status": "ready"
}
```

---

## Decision Endpoint

```http
POST /v1/decisions
```

This is the primary decision-engine endpoint.

Example request:

```json
{
  "session_id": "00000000-0000-0000-0000-000000000001",
  "anonymous_actor_id": "actor-normal",
  "client_version": "1.0.0-web",
  "slip_id": "slip-normal",
  "interaction": {
    "selection_changes": 0,
    "stake_changes": 0,
    "odds_changed": true,
    "time_since_slip_creation_seconds": 18.5,
    "confirmation_attempts": 0,
    "interaction_velocity": 0.0,
    "recent_backtracks": 0,
    "dwell_time_seconds": 18.5
  }
}
```

Example response:

```json
{
  "decision_id": "...",
  "action": "EXPLAIN_ODDS_CHANGE",
  "state": "ODDS_CHANGE",
  "confidence": 0.95,
  "reason": "...",
  "response_text": "...",
  "policy_version": "...",
  "model_version": "...",
  "action_registry_version": "...",
  "safety_status": "SAFE"
}
```

---

# 14. Repository Structure

```text
Confidence-layer/
│
├── src/
│   └── confidence/
│       │
│       ├── api/
│       │   ├── app.py
│       │   ├── routes.py
│       │   ├── models.py
│       │   └── dependencies.py
│       │
│       ├── application/
│       │   ├── engine.py
│       │   ├── context_builder.py
│       │   └── ...
│       │
│       ├── domain/
│       │   ├── enums.py
│       │   ├── models.py
│       │   ├── events.py
│       │   ├── actions.py
│       │   ├── safety.py
│       │   ├── state.py
│       │   ├── policy.py
│       │   └── response.py
│       │
│       ├── infrastructure/
│       │   ├── persistence.py
│       │   └── providers.py
│       │
│       ├── db/
│       │   ├── schema.py
│       │   └── connection.py
│       │
│       ├── ui/
│       │   ├── index.html
│       │   └── app.js
│       │
│       ├── config.py
│       └── log.py
│
├── tests/
│   ├── test_domain.py
│   ├── test_events.py
│   ├── test_actions.py
│   ├── test_safety_contract.py
│   ├── test_engine.py
│   ├── test_api.py
│   └── ...
│
├── alembic/
│   ├── env.py
│   └── versions/
│
├── docs/
│   ├── ADR-001-ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   └── IMPLEMENTATION_AUDIT.md
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── .env.example
└── README.md
```

---

# 15. Technology Stack

## Backend

```text
Python 3.12+
FastAPI
Pydantic
SQLAlchemy
Alembic
PostgreSQL
```

## Engineering

```text
pytest
pytest-asyncio
mypy
ruff
HTTPX
Docker
Docker Compose
```

## Observability

```text
structlog
OpenTelemetry
```

## Frontend

The demonstration UI intentionally avoids a separate frontend build system.

```text
HTML
JavaScript
TailwindCSS
FastAPI StaticFiles
```

The Tailwind CSS demonstration dependency is loaded by the demo page; this is suitable for the hackathon prototype but should be replaced by an appropriate controlled asset strategy for production.

---

# 16. Team Setup Guide

This section is intended for a new teammate who has just cloned the repository.

## Step 1 — Install prerequisites

Install:

```text
Python 3.12+
Git
Docker
Docker Compose
```

Verify:

```bash
python --version
git --version
docker --version
docker compose version
```

---

## Step 2 — Clone the repository

```bash
git clone https://github.com/Saisharathchandranandnetha/Confidence-layer.git
cd Confidence-layer
```

---

## Step 3 — Create a virtual environment

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## Step 4 — Install dependencies

```bash
pip install -e ".[dev]"
```

Or:

```bash
make install
```

---

## Step 5 — Configure environment

Copy:

```bash
cp .env.example .env
```

Review `.env` before running the application.

Do not commit:

```text
.env
credentials
API keys
production secrets
real customer data
```

---

# 17. Database Setup

Start PostgreSQL:

```bash
make db-up
```

Run migrations:

```bash
make db-migrate
```

Verify the service:

```bash
docker compose ps
```

The database is used for persistence/audit functionality.

---

# 18. Run the Application

For local development:

```bash
uvicorn confidence.api.app:app --reload --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000/
```

API:

```text
http://localhost:8000/docs
```

Health:

```text
http://localhost:8000/health
```

Readiness:

```text
http://localhost:8000/ready
```

---

# 19. Run Everything with Docker

Start the complete stack:

```bash
make docker-up
```

or:

```bash
docker compose up --build
```

Stop it:

```bash
make docker-down
```

or:

```bash
docker compose down
```

---

# 20. Development Commands

The Makefile provides the standard team workflow.

### Install

```bash
make install
```

### Run tests

```bash
make test
```

### Lint

```bash
make lint
```

### Format

```bash
make format
```

### Type checking

```bash
make typecheck
```

### Complete validation

```bash
make check
```

`make check` should be the minimum validation before pushing changes.

---

# 21. Testing Philosophy

The project treats safety behavior as a contract.

Tests should verify not only:

> "Does the system produce the expected action?"

but also:

> **"Can the system ever produce an unsafe action under the tested conditions?"**

Testing areas include:

```text
Domain validation
Event validation
Action registry
Safety invariants
Decision engine
API behavior
Provider failures
Missing data
Low-confidence states
Legitimate reconsideration
Self-exclusion
Harm states
End-to-end scenarios
```

Run:

```bash
make test
```

Before submitting a change:

```bash
make check
```

---

# 22. Failure Handling

Confidence Layer follows a fail-closed strategy.

If a critical dependency fails:

```text
Safety unavailable
       ↓
NO_INTERVENTION
```

If authoritative market information is unavailable:

```text
Cannot verify fact
       ↓
Do not fabricate explanation
       ↓
NO_INTERVENTION
```

If state confidence is insufficient:

```text
Uncertain classifier
       ↓
NO_INTERVENTION
```

If the decision process exceeds its configured time budget:

```text
Timeout
       ↓
NO_INTERVENTION
```

The system prefers an omitted intervention over an unsafe or fabricated intervention.

---

# 23. Authoritative Data Boundary

The system distinguishes between:

### Authoritative information

Examples:

```text
Safety status
Self-exclusion
Protective restrictions
Market definition
Current odds
Odds history
Slip configuration
```

and:

### Client telemetry

Examples:

```text
Dwell time
Backtracks
Stake changes
Interaction velocity
```

Client telemetry can help identify behavioral context, but critical safety and factual information must not be trusted solely from mutable client input.

---

# 24. Deterministic Response Generation

The current prototype does not require an LLM in the critical decision path.

Responses are generated from:

```text
Validated context
        +
Approved action
        +
Approved template
```

This avoids allowing a language model to:

* invent odds
* calculate authoritative financial values
* determine eligibility
* override safety
* create arbitrary interventions
* reinterpret safety restrictions

An LLM may be considered in a future version for controlled copy transformation **after** factual content has already been assembled and validated.

---

# 25. Why There Is No Online Bandit Yet

Confidence Layer intentionally does not use online reinforcement learning or unconstrained contextual-bandit exploration in the initial prototype.

The order is:

```text
Safety
  ↓
Deterministic state
  ↓
Deterministic policy
  ↓
Evaluation
  ↓
Offline policy optimization
  ↓
Constrained adaptive policy
```

A future adaptive policy must remain subordinate to the safety authority.

The system must never "learn" that an unsafe action improves a business metric and subsequently select it.

---

# 26. Security Principles

The prototype is designed around several security assumptions.

### Never trust critical client state

Critical facts should come from authoritative services.

### Fail closed

Dependency failure should not silently become permission to intervene.

### Version decisions

Decisions should retain policy/action/model provenance.

### Audit decisions

The system should be able to answer:

```text
What did we know?
What did we decide?
Why?
Which policy version?
Which action version?
What safety state?
```

### Protect tenant/user boundaries

Production implementations must enforce strict isolation between users, sessions, and operators.

---

# 27. Observability

A production implementation should make every decision explainable.

A decision should be traceable to:

```text
Session
Actor
Timestamp
Input context
Safety state
Detected state
Confidence
Eligible actions
Selected action
Policy version
Model version
Action registry version
Decision reason
Outcome
```

This creates an audit trail rather than an opaque recommendation engine.

---

# 28. Demo Checklist

Before a hackathon presentation:

```bash
make check
```

Then:

```bash
make db-up
make db-migrate
```

Start:

```bash
uvicorn confidence.api.app:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/
```

Test these scenarios:

```text
☐ Normal user
☐ Odds changed
☐ User backtracked
☐ Harmful play
☐ Self-excluded
☐ Safety service failure
☐ Missing odds history
☐ Market service failure
```

Verify:

```text
☐ Pipeline visualization works
☐ JSON result appears
☐ Intervention appears only when appropriate
☐ NO_INTERVENTION appears for blocked scenarios
☐ No console/server errors
```

---

# 29. Recommended Live Demo Sequence

For a 10–15 minute technical demonstration:

### 1. Start with the problem

Explain:

> "Not every abandoned betslip should be recovered."

### 2. Show normal interaction

Demonstrate the mock betslip.

### 3. Trigger odds movement

Show:

```text
Client signal
    ↓
Safety
    ↓
State = ODDS_CHANGE
    ↓
Policy
    ↓
EXPLAIN_ODDS_CHANGE
```

### 4. Trigger legitimate reconsideration

Show:

```text
Backtrack
    ↓
LEGITIMATE_RECONSIDERATION
    ↓
NO_INTERVENTION
```

Explain:

> "The system is allowed to leave the user alone."

### 5. Trigger harmful play

Show:

```text
HARMFUL_PLAY
    ↓
Safety gate
    ↓
NO_INTERVENTION
```

### 6. Break the safety service

Show:

```text
Safety dependency failure
    ↓
Fail closed
    ↓
NO_INTERVENTION
```

### 7. Break the market dependency

Show:

```text
Missing authoritative data
    ↓
No fabricated explanation
    ↓
NO_INTERVENTION
```

### 8. Finish with the architecture

Return to:

```text
Safety → State → Policy → Final Safety Check
```

---

# 30. What This Prototype Demonstrates

The prototype demonstrates the architectural feasibility of:

* context-aware betslip decision support
* uncertainty classification
* safety-first intervention gating
* deterministic policy selection
* authoritative dependency handling
* fail-closed behavior
* auditable decisions
* reproducible scenarios
* interactive visualization
* safe `NO_INTERVENTION` outcomes

It does **not** demonstrate statistically validated customer uplift.

---

# 31. Current Limitations

This is a hackathon prototype.

Important limitations include:

### Synthetic data

No production customer dataset is included.

### Dummy providers

Real operator services are represented by interfaces and deterministic mocks.

### Deterministic state logic

The current prototype prioritizes explainability and safety over learned personalization.

### No production-scale infrastructure

Kafka, Redis, Kubernetes, distributed feature stores, and similar infrastructure are intentionally excluded from the prototype.

### No real-world baseline

There is currently no operator baseline against which uplift can responsibly be claimed.

### No production regulatory certification

The prototype is not a production gambling system and has not undergone operator/legal/regulatory approval.

---

# 32. Phase 4 — Evaluation

The next major phase is evaluation.

The evaluation layer should establish whether the system is actually doing what it claims.

Key questions:

```text
Can uncertainty be classified accurately?

Can legitimate reconsideration be distinguished from
resolvable information gaps?

How often does the system intervene incorrectly?

How often does it correctly choose NO_INTERVENTION?

Are safety constraints preserved under every scenario?

Does factual clarification improve decision quality
without creating pressure?

Does the system remain safe when dependencies fail?
```

---

## Planned Evaluation

### Classification

Evaluate:

```text
Precision
Recall
F1
Confusion matrix
Calibration
```

### Safety

Measure:

```text
Unsafe intervention rate
False-positive intervention rate
Safety-block accuracy
Fail-closed coverage
```

### Decision quality

Measure:

```text
Resolvable uncertainty correctly identified
Legitimate reconsideration preserved
Unsupported intervention avoided
NO_INTERVENTION correctness
```

### Policy

Evaluate policies offline before any adaptive deployment.

---

# 33. Roadmap

```text
Phase 1
Domain + Safety Foundation
        │
        ▼
Phase 2
Deterministic Decision Engine
        │
        ▼
Phase 3
Interactive Demonstration Layer
        │
        ▼
Phase 4
Evaluation + Scenario Benchmarking
        │
        ▼
Phase 5
Offline Policy Optimization
        │
        ▼
Phase 6
Constrained Adaptive Policy
        │
        ▼
Production Integration
```

Adaptive optimization should only be considered after strong offline evaluation and safety validation.

---

# 34. Team Workflow

For a multi-person team, changes should be organized by responsibility.

## Recommended ownership

### Backend / Decision Engine

Responsible for:

```text
src/confidence/application/
src/confidence/domain/
src/confidence/api/
```

### Safety

Responsible for:

```text
SafetyContract
SafetyProvider
Safety tests
Failure modes
Safety invariants
```

### Evaluation / ML

Responsible for:

```text
evals/
ml/
scenario datasets
classification evaluation
policy evaluation
```

### Frontend / Demo

Responsible for:

```text
src/confidence/ui/
demo scenarios
visual pipeline
presentation flow
```

### Infrastructure

Responsible for:

```text
Docker
PostgreSQL
Alembic
CI/CD
observability
deployment
```

---

# 35. Team Contribution Rules

Before pushing code:

```bash
make check
```

Every feature should include tests.

Every safety behavior should include an explicit safety test.

Avoid introducing infrastructure unless the current prototype actually requires it.

Do not bypass the safety authority to simplify implementation.

Do not add an intervention directly to the UI without registering it in the Action Registry.

Do not introduce LLM-generated facts into the critical decision path.

Do not use synthetic demo behavior as evidence of real-world business impact.

---

# 36. Pull Request Checklist

Before opening a PR:

```text
☐ Tests added/updated
☐ make check passes
☐ Safety behavior reviewed
☐ Failure behavior reviewed
☐ No secrets committed
☐ No real customer data
☐ API contract preserved
☐ Action Registry updated if needed
☐ Documentation updated
☐ Demo scenario updated if applicable
```

For safety-sensitive changes:

```text
☐ Explicit safety invariant added
☐ Positive-path test
☐ Blocked-path test
☐ Dependency-failure test
☐ Regression test
```

---

# 37. Troubleshooting

## Port 8000 already in use

Find the process:

```bash
lsof -i :8000
```

or:

```bash
ss -ltnp | grep 8000
```

Then stop the conflicting process or start the application on another port.

---

## PostgreSQL is not running

Check:

```bash
docker compose ps
```

Start it:

```bash
make db-up
```

---

## Migration errors

Check the database container:

```bash
docker compose logs postgres
```

Then retry:

```bash
make db-migrate
```

---

## UI does not load

Check:

```text
http://localhost:8000/health
```

If the API works but the UI does not, verify:

```text
src/confidence/ui/index.html
src/confidence/ui/app.js
```

The application should mount the UI under:

```text
/ui
```

---

## Tests fail after pulling changes

Reinstall dependencies:

```bash
pip install -e ".[dev]"
```

Then:

```bash
make check
```

---

# 38. Architectural Principles

Confidence Layer follows these principles:

### 1. Safety before optimization

```text
Safety > Policy > Business objective
```

### 2. No pressure

The system should resolve uncertainty, not manufacture urgency.

### 3. Abandonment can be correct

A successful decision may be:

```text
NO_INTERVENTION
```

### 4. Facts must be authoritative

Do not fabricate unavailable market information.

### 5. Fail closed

Unknown safety is not permission.

### 6. Deterministic first

Establish correctness before introducing adaptive optimization.

### 7. Explainable decisions

Every decision should have a reason and provenance.

### 8. Minimize infrastructure

Only introduce infrastructure when the problem actually requires it.

---

# 39. Hackathon Positioning

Confidence Layer is not positioned as:

> "An AI system that makes users place more bets."

It is positioned as:

> **A safety-constrained decision-quality layer that determines when a user's hesitation represents resolvable uncertainty and provides only appropriate factual clarification — while treating safe abandonment as a valid outcome.**

The technical differentiator is the separation of:

```text
Safety Authority
        +
State Authority
        +
Policy Authority
```

with safety acting as a hard constraint.

---

# 40. Final Mental Model

The entire system can be reduced to one question:

```text
                    USER HESITATES
                          │
                          ▼
                 ┌─────────────────┐
                 │  Is intervention │
                 │      SAFE?       │
                 └────────┬────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
               NO                  YES
                │                   │
                ▼                   ▼
        NO_INTERVENTION      WHAT IS HAPPENING?
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ Is there a safe │
                           │ factual action? │
                           └────────┬────────┘
                                    │
                           ┌────────┴────────┐
                           │                 │
                          NO                YES
                           │                 │
                           ▼                 ▼
                   NO_INTERVENTION    APPROVED ACTION
                                             │
                                             ▼
                                      FINAL SAFETY CHECK
                                             │
                                             ▼
                                          RESPONSE
```

**Confidence Layer does not try to eliminate every abandonment.**

It tries to make the system better at knowing **when to help, when not to help, and why.**

---

## License

This repository is a hackathon prototype.

Add the project's final license here before public production reuse.

---

## Acknowledgements

Built for the **FEG Innovation Hackathon 2026 — Challenge 1**.

**Project:** Confidence Layer

**Purpose:** Safety-constrained decision support for betslip uncertainty.

---

## Quick Reference

```bash
# Clone
git clone https://github.com/Saisharathchandranandnetha/Confidence-layer.git
cd Confidence-layer

# Environment
python -m venv .venv
source .venv/bin/activate

# Install
pip install -e ".[dev]"

# Database
make db-up
make db-migrate

# Validate
make check

# Run
uvicorn confidence.api.app:app --reload --host 0.0.0.0 --port 8000

# Demo
# http://localhost:8000/

# API
# http://localhost:8000/docs
```

**If `make check` passes and the demo opens at `/`, the local development environment is ready.**


## Production Architecture (Phase 4)
- **Infrastructure**: Kafka (Redpanda) for events/audit, Redis for idempotency/state, PostgreSQL for persistence.
- **Resilience**: Circuit breakers, timeouts, rate limiting.
- **Security**: OAuth2 Bearer token authentication, Zero-PII by design.
- **Observability**: OpenTelemetry tracing, Prometheus metrics.
- **Deployment**: Kubernetes ready with liveness/readiness probes.
