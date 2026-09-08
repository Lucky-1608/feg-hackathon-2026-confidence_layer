# ADR-001: Architecture — Confidence Layer

**Status:** Accepted
**Date:** 2026-09-03
**Decision makers:** Principal Engineer

---

## Context

Confidence Layer is an FEG Innovation Hackathon 2026 Challenge 1 prototype. It addresses the problem of **user uncertainty during betslip confirmation** in sports betting platforms.

The core hypothesis is:

> When a user hesitates during betslip confirmation, the system can distinguish between different types of uncertainty (information gaps, legitimate reconsideration, potential harm) and provide contextually appropriate interventions — or deliberately choose not to intervene — improving user experience without compromising safety.

This ADR establishes the foundational architecture for the implementation.

---

## Decision

### 1. Three-Authority Architecture

The system is decomposed into three logically independent authorities:

| Authority | Question | Owns |
|-----------|----------|------|
| **Safety Authority** | "Can we intervene?" | Self-exclusion, protective restrictions, harm-state, fail-closed |
| **State Authority** | "What is happening?" | Uncertainty classification, confidence estimation |
| **Policy Authority** | "Which safe action?" | Selection from pre-approved action set |

**Rationale:** Separating safety from utility prevents the common anti-pattern where safety becomes a penalty term in an optimization objective. Safety must be a hard gate, not a soft signal.

### 2. Safety-Before-Optimization Pipeline

```
SAFETY → ELIGIBILITY → SAFE ACTION SET → UTILITY/POLICY
```

The optimizer never sees unsafe actions. This is structurally different from:

```
utility - harm  (REJECTED)
```

**Rationale:** A penalty-based approach can always find edge cases where "high enough utility" overrides safety. A gating approach makes this structurally impossible.

### 3. NO_INTERVENTION as First-Class Action

`NO_INTERVENTION` is a deliberate, audited action — not an error state or absence of action. It is the default when the system cannot confidently and safely intervene.

**Rationale:** The system must prove it should intervene, not prove it shouldn't. This inverts the typical conversion-optimization assumption.

### 4. Rule-Based First, ML Later

Phase 1–4 use deterministic rule-based state estimation and policy selection. ML (Phase 5+) is introduced behind an interface and must demonstrably improve over the rule-based baseline.

**Rationale:**
- Rules are auditable and debuggable
- Rules establish a quantified baseline
- ML without a baseline is unmeasurable
- Hackathon time constraints favor working rules over untrained models

### 5. Monolithic Application, Modular Domain

The system is deployed as a single Python application (FastAPI) with clearly separated domain modules. No microservice decomposition.

**Rationale:**
- A monolith eliminates network partitioning, distributed transaction, and service discovery complexity
- Module boundaries enforce separation of concerns without operational overhead
- Can be decomposed later if needed (modular monolith pattern)

### 6. Purpose-Specific State and Delivery Adapters

PostgreSQL is the durable relational store, Redis supports ephemeral session/idempotency state, and Kafka/Redpanda provides event-delivery boundaries. The domain and application layers depend on ports rather than these implementations.

**Rationale:**
- ACID guarantees for audit trail integrity
- Foreign keys enforce referential integrity between sessions, events, and decisions
- JSONB supports flexible context storage without schema explosion
- Explicit adapter boundaries keep infrastructure replaceable and testable

### 7. Template-Based Response Generation

All user-facing content is generated from controlled templates with validated factual data. No LLM in the response path.

**Rationale:**
- Factual values (odds, stakes, returns) must be deterministically correct
- Template validation is testable and auditable
- LLM hallucination risk is unacceptable for financial information

### 8. Fail-Closed Safety

Every failure mode defaults to `NO_INTERVENTION`:
- Safety service unavailable → NO_INTERVENTION
- Model unavailable → NO_INTERVENTION
- Database unavailable → NO_INTERVENTION
- Timeout → NO_INTERVENTION
- Unknown state → NO_INTERVENTION

**Rationale:** In a safety-critical system handling gambling decisions, the worst failure is a *wrong* intervention. Doing nothing is always safe.

---

## Architecture Diagram

```
Client (Betslip UI)
        │
        ▼
   ┌─────────┐
   │ API      │  POST /v1/events, /v1/decisions
   │ Layer    │  Validation, authentication, idempotency
   └────┬────┘
        │
        ▼
   ┌──────────────┐
   │ Decision     │  Orchestrates the full pipeline
   │ Engine       │
   └──┬───────────┘
      │
      ├──► Context Builder ──► Session, Slip, Market, Safety, Interaction
      │
      ├──► Safety Gateway ──► SAFE / BLOCKED / UNKNOWN
      │         │
      │         └── Self-exclusion, Harm state, Protective restrictions
      │
      ├──► State Estimator ──► UncertaintyState + Confidence
      │         │
      │         └── Rules (V1) → ML interface (V2+)
      │
      ├──► Eligibility Filter ──► Safe Action Set
      │         │
      │         └── Intersect: safety result × state × action registry
      │
      ├──► Policy Selector ──► Selected Action
      │         │
      │         └── Choose from safe action set only
      │
      ├──► Final Safety Check ──► Validate selected action
      │
      ├──► Response Generator ──► Template + validated facts
      │
      └──► Audit Writer ──► Full decision provenance
                │
                ▼
           PostgreSQL
```

---

## Consequences

### Positive
- Safety is structurally guaranteed, not probabilistically managed
- System is auditable and reproducible from stored provenance
- Rule-based baseline is immediately testable
- Single deployment unit minimizes operational complexity
- NO_INTERVENTION default eliminates harmful failure modes

### Negative
- Monolith must be carefully modularized to prevent coupling
- Rule-based estimation may miss subtle behavioral patterns (addressed by ML in Phase 5)
- Template-based responses may feel less natural than LLM-generated (acceptable for factual accuracy)
- Single PostgreSQL is a SPOF (acceptable for hackathon; addressed by replication in production)

### Risks
- If rule-based estimation has poor precision, the demo may show too many NO_INTERVENTION results
  - Mitigation: carefully tuned rules for demo scenarios; evaluation framework quantifies this
- If safety invariants are too strict, the system may never intervene
  - Mitigation: scenario registry explicitly includes cases where intervention IS appropriate

---

## Compliance with Architecture Spec

| Requirement | Status |
|-------------|--------|
| Safety ≠ negative reward | ✅ Gating architecture |
| Three authorities | ✅ Safety, State, Policy |
| NO_INTERVENTION first-class | ✅ Default action |
| 17 system invariants | ✅ Implemented as executable tests |
| No LLM in decision path | ✅ Template-based responses |
| No Kafka/Redis/K8s | ✅ Not included |
| Fail-closed | ✅ All failure → NO_INTERVENTION |
| Auditable decisions | ✅ Full provenance stored |
| p95 < 100ms target | ✅ Measured, not assumed |
