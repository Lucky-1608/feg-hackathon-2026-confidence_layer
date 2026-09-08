# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 35 files · ~20,611 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 489 nodes · 1190 edges · 17 communities (12 shown, 2 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 170 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Safety Authority & Invariants
- Action Registry & Definitions
- API Dependencies & Context Providers
- Decision Engine & API Models
- Application Engine & Domain Models
- Market Context & Harm Indicators
- FastAPI App & Database Session
- Database Schema & Alembic Tests
- Domain Events & Schema Validation
- Domain Model & Safety Tests
- Interactive UI & Client Telemetry
- Conversion Safety Rules
- Package Init (Confidence)
- Confidence Layer Root

## God Nodes (most connected - your core abstractions)
1. `SafetyContract` - 56 edges
2. `ActionRegistry` - 56 edges
3. `ActionId` - 43 edges
4. `DecisionEngine` - 38 edges
5. `UncertaintyState` - 35 edges
6. `SafetyContext` - 31 edges
7. `StateEstimate` - 29 edges
8. `DecisionRequest` - 28 edges
9. `DecisionContext` - 28 edges
10. `NoInterventionReason` - 27 edges

## Surprising Connections (you probably didn't know these)
- `TestDecision` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_domain.py → src/confidence/domain/enums.py
- `TestAdversarialAndFailures` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/enums.py
- `TestEndToEndScenarios` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/enums.py
- `TestPropertyInvariants` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/enums.py
- `TestSafetyResult` --uses--> `SafetyBlockReason`  [INFERRED]
  tests/test_domain.py → src/confidence/domain/enums.py

## Import Cycles
- None detected.

## Communities (17 total, 2 thin omitted)

### Community 0 - "Safety Authority & Invariants"
Cohesion: 0.07
Nodes (42): NoInterventionReason, Result of the Safety Authority's evaluation. SAFE: intervention is permitted.…, Why the Safety Authority blocked an intervention., Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no…, SafetyBlockReason, SafetyStatus, Safety-relevant state, sourced from authoritative server-side systems. These…, Output of the Safety Authority. The Safety Authority answers: 'Can we… (+34 more)

### Community 1 - "Action Registry & Definitions"
Cohesion: 0.06
Nodes (27): get_response_generator(), ActionDefinition, ActionRegistry, BaseModel, Return all registered action IDs., Definition of a single registered action. Each action declares: - which…, In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Get an action definition by ID. (+19 more)

### Community 2 - "API Dependencies & Context Providers"
Cohesion: 0.06
Nodes (42): DummyMarketProvider, DummySlipProvider, get_action_registry(), get_context_builder(), get_decision_engine(), get_engine(), get_persistence_provider(), get_policy_selector() (+34 more)

### Community 3 - "Decision Engine & API Models"
Cohesion: 0.08
Nodes (33): asyncio, post, DummySafetyProvider, CreateDecisionRequest, DecisionResponse, InteractionDataPayload, BaseModel, API Data Models. Defines the external API request and response schemas. These… (+25 more)

### Community 4 - "Application Engine & Domain Models"
Cohesion: 0.08
Nodes (33): Decision Engine Orchestrator. Coordinates the complete end-to-end pipeline: 1.…, Versioned Action Registry for the Confidence Layer. The Action Registry is the…, ActionCategory, OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Types of outcomes following a decision., Possible states of user uncertainty during betslip confirmation. The State…, Semantic categories for actions. (+25 more)

### Community 5 - "Market Context & Harm Indicators"
Cohesion: 0.07
Nodes (43): HarmIndicators, MarketContext, OddsSnapshot, BaseModel, A point-in-time odds value from an authoritative source., A single selection within a betslip., Authoritative market data for a selection., Behavioral indicators of potential gambling harm. These are derived from… (+35 more)

### Community 6 - "FastAPI App & Database Session"
Cohesion: 0.06
Nodes (40): Any, async_sessionmaker, AsyncSession, Engine, FastAPI, sessionmaker, create_app(), FastAPI application entrypoint. (+32 more)

### Community 7 - "Database Schema & Alembic Tests"
Cohesion: 0.08
Nodes (11): Alembic environment configuration., Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online(), Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times. (+3 more)

### Community 8 - "Domain Events & Schema Validation"
Cohesion: 0.16
Nodes (11): field_validator, EventType, Types of client events the system processes., ConfidenceEvent, BaseModel, Versioned event schema for the Confidence Layer. Events are the primary input…, A versioned event from the client. Schema follows the architecture spec's event…, datetime (+3 more)

### Community 9 - "Domain Model & Safety Tests"
Cohesion: 0.11
Nodes (11): A user's betslip confirmation session., Session, datetime, Tests for domain model validation. Verifies that all Pydantic domain models…, TestDecision, TestOutcome, TestSafetyContext, TestSafetyResult (+3 more)

### Community 10 - "Interactive UI & Client Telemetry"
Cohesion: 0.22
Nodes (5): dwellTimer, evaluateDecision(), sessionId, telemetry, updatePipeline()

### Community 11 - "Conversion Safety Rules"
Cohesion: 0.36
Nodes (3): Return True if an action is conversion-oriented. NO_INTERVENTION and…, Test which actions are classified as conversion-oriented., TestConversionOrientation

## Knowledge Gaps
- **4 isolated node(s):** `dwellTimer`, `sessionId`, `telemetry`, `confidence-layer`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 185 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ActionRegistry` connect `Action Registry & Definitions` to `API Dependencies & Context Providers`, `Decision Engine & API Models`, `Application Engine & Domain Models`, `Market Context & Harm Indicators`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `SafetyContract` connect `Safety Authority & Invariants` to `Action Registry & Definitions`, `API Dependencies & Context Providers`, `Decision Engine & API Models`, `Application Engine & Domain Models`, `Market Context & Harm Indicators`, `Conversion Safety Rules`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `ActionId` connect `Action Registry & Definitions` to `Safety Authority & Invariants`, `API Dependencies & Context Providers`, `Decision Engine & API Models`, `Application Engine & Domain Models`, `Domain Model & Safety Tests`, `Conversion Safety Rules`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `SafetyContract` (e.g. with `get_decision_engine()` and `DecisionEngine`) actually correct?**
  _`SafetyContract` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ActionRegistry` (e.g. with `get_decision_engine()` and `get_response_generator()`) actually correct?**
  _`ActionRegistry` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `DecisionEngine`) actually correct?**
  _`ActionId` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `DecisionEngine` (e.g. with `create_decision()` and `ContextBuilder`) actually correct?**
  _`DecisionEngine` has 15 INFERRED edges - model-reasoned connections that need verification._