# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 63 files · ~43,329 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 680 nodes · 1147 edges · 68 communities (36 shown, 29 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 108 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a1fef1b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StateEstimate
- ActionId
- ContextBuilder
- DecisionEngine
- UncertaintyState
- conftest.py
- config.py
- TestSchemaCreation
- ConfidenceEvent
- test_domain.py
- Interactive UI & Client Telemetry
- .is_conversion_oriented
- Package Init (Confidence)
- Confidence Layer Root
- What You Must Do When Invoked
- What You Must Do When Invoked
- DecisionRequest
- dependencies.py
- engine.py
- ActionRegistry
- domain/__init__.py
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- DummySafetyProvider
- PersistenceProvider
- graphify reference: query, path, explain
- env.py
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- DatabasePersistenceProvider
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rules/graphify.md
- .agents/skills/graphify/references/extraction-spec.md
- workflows/graphify.md
- CLAUDE.md
- .claude/CLAUDE.md
- .claude/skills/graphify/references/extraction-spec.md
- application/__init__.py
- SafetyContract
- Protocol
- DecisionContext
- api/models.py
- .get_safety_context
- .get_market_context
- .get_slip_context
- MarketContext
- MarketProvider
- SafetyContext
- SafetyProvider
- SlipContext
- SlipProvider
- ContextBuilder
- BaseModel
- ContextBuilder
- Protocol
- UUID
- fixture

## God Nodes (most connected - your core abstractions)
1. `DecisionEngine` - 32 edges
2. `DecisionRequest` - 29 edges
3. `StateEstimate` - 29 edges
4. `ActionId` - 26 edges
5. `UncertaintyState` - 19 edges
6. `SafetyContract` - 17 edges
7. `ActionDefinition` - 17 edges
8. `HarmIndicators` - 17 edges
9. `ConfidenceEvent` - 17 edges
10. `ActionRegistry` - 16 edges

## Surprising Connections (you probably didn't know these)
- `TestAdversarialAndFailures` --uses--> `DummySafetyProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestEndToEndScenarios` --uses--> `DummySafetyProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestPropertyInvariants` --uses--> `DummySafetyProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestEndToEndScenarios` --uses--> `DummySlipProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestPropertyInvariants` --uses--> `DummySlipProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py

## Import Cycles
- None detected.

## Communities (68 total, 29 thin omitted)

### Community 0 - "StateEstimate"
Cohesion: 0.08
Nodes (25): Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, TestStateEstimate, datetime, SafetyContext, SafetyContract, Tests for the Safety Contract. Verifies all 17 system invariants (S1–S17) as…, S4: Unknown safety state → fail closed. (+17 more)

### Community 1 - "ActionId"
Cohesion: 0.10
Nodes (21): ActionDefinition, ActionRegistry, BaseModel, Versioned Action Registry for the Confidence Layer. The Action Registry is the…, Return all registered action IDs., Definition of a single registered action. Each action declares: - which…, In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Get an action definition by ID. (+13 more)

### Community 2 - "ContextBuilder"
Cohesion: 0.23
Nodes (13): Protocol, ContextBuilder, Context Builder. Constructs the DecisionContext from the incoming request and…, Builds a complete, trustworthy DecisionContext., MarketProvider, Domain Ports (Protocols). The domain owns its interfaces (hexagonal…, Provides authoritative safety state for a session/user., Provides authoritative betslip state. (+5 more)

### Community 3 - "DecisionEngine"
Cohesion: 0.07
Nodes (35): asyncio, BaseModel, NoInterventionReason, post, CreateDecisionRequest, External request payload for a new decision., create_decision(), API routes for the Confidence Layer. (+27 more)

### Community 4 - "UncertaintyState"
Cohesion: 0.16
Nodes (10): Return actions eligible for a given state and available data. An action is…, Possible states of user uncertainty during betslip confirmation. The State…, UncertaintyState, DecisionContext, Complete context assembled by the Context Builder for a decision. This is the…, Generate response based on the selected action and available context., State Authority. Classifies user uncertainty during betslip confirmation into a…, Deterministic rule-based state estimator. Evaluates the decision context and… (+2 more)

### Community 5 - "conftest.py"
Cohesion: 0.07
Nodes (46): HarmIndicators, MarketContext, OddsSnapshot, BaseModel, Safety-relevant state, sourced from authoritative server-side systems. These…, A user's betslip confirmation session., A point-in-time odds value from an authoritative source., State of the betslip at decision time. (+38 more)

### Community 6 - "config.py"
Cohesion: 0.06
Nodes (40): Any, async_sessionmaker, AsyncSession, Engine, FastAPI, sessionmaker, create_app(), lifespan() (+32 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "ConfidenceEvent"
Cohesion: 0.19
Nodes (8): field_validator, ConfidenceEvent, BaseModel, A versioned event from the client. Schema follows the architecture spec's event…, datetime, Tests for the event schema. Verifies event validation, required fields,…, Every EventType enum value should produce a valid event., TestConfidenceEvent

### Community 9 - "test_domain.py"
Cohesion: 0.08
Nodes (17): SlipContext, A single selection within a betslip., Selection, datetime, DecisionContext, Session, SlipContext, Tests for domain model validation. Verifies that all Pydantic domain models… (+9 more)

### Community 10 - "Interactive UI & Client Telemetry"
Cohesion: 0.22
Nodes (5): dwellTimer, evaluateDecision(), sessionId, telemetry, updatePipeline()

### Community 11 - ".is_conversion_oriented"
Cohesion: 0.36
Nodes (3): Return True if an action is conversion-oriented. NO_INTERVENTION and…, Test which actions are classified as conversion-oriented., TestConversionOrientation

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 20 - "dependencies.py"
Cohesion: 0.18
Nodes (16): get_action_registry(), get_decision_engine(), get_engine(), get_persistence_provider(), get_policy_selector(), get_response_generator(), get_safety_contract(), get_state_estimator() (+8 more)

### Community 21 - "engine.py"
Cohesion: 0.33
Nodes (4): Decision Engine Orchestrator. Coordinates the complete end-to-end pipeline: 1.…, Persistence for audit logs and decisions. Architectural constraint: Persistence…, Structured logging for the Confidence Layer. Uses structlog for JSON-formatted,…, UUID

### Community 22 - "ActionRegistry"
Cohesion: 0.11
Nodes (10): ActionRegistry, Tests for the Action Registry. Verifies: - All 6 initial actions are registered…, When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be…, Disabled actions should not appear in eligible lists., NO_INTERVENTION must be eligible for every possible state., When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible., TestActionDefinitions, TestActionEligibility (+2 more)

### Community 23 - "domain/__init__.py"
Cohesion: 0.16
Nodes (19): EventType, OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Types of outcomes following a decision., Result of the Safety Authority's evaluation. SAFE: intervention is permitted.…, Why the Safety Authority blocked an intervention., Types of client events the system processes., SafetyBlockReason (+11 more)

### Community 24 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 25 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 26 - "DummySafetyProvider"
Cohesion: 0.16
Nodes (12): fixture, DummyMarketProvider, DummySafetyProvider, DummySlipProvider, get_context_builder(), MarketContext, SafetyContext, UUID (+4 more)

### Community 27 - "PersistenceProvider"
Cohesion: 0.14
Nodes (11): ActionRegistry, PolicySelector, ResponseGenerator, SafetyContract, StateEstimator, PersistenceProvider, Decision, DecisionContext (+3 more)

### Community 28 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 29 - "env.py"
Cohesion: 0.33
Nodes (5): Alembic environment configuration. Loads database URL from environment…, Run migrations in 'offline' mode., Run migrations in 'online' mode., run_migrations_offline(), run_migrations_online()

### Community 30 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 31 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 32 - "graphify reference: commit hook and native AGENTS.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 33 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 34 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 35 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 36 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 37 - "DatabasePersistenceProvider"
Cohesion: 0.25
Nodes (6): DatabasePersistenceProvider, AsyncEngine, Decision, DecisionContext, Saves decisions and audit records asynchronously to the database. All column…, Persist a decision and its audit log to the database. Called as a background…

### Community 49 - "SafetyContract"
Cohesion: 0.13
Nodes (13): NoInterventionReason, Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no…, Output of the Safety Authority. The Safety Authority answers: 'Can we…, SafetyResult, datetime, Safety Contract for the Confidence Layer. Encodes system invariants S1–S17 as…, Check if state estimation confidence is sufficient. S4: Unknown safety state →…, Check if user is legitimately reconsidering. The system must never assume… (+5 more)

### Community 51 - "DecisionContext"
Cohesion: 0.22
Nodes (5): DecisionContext, Harm > everything else., TestPolicySelector, TestResponseGenerator, TestStateEstimator

### Community 52 - "api/models.py"
Cohesion: 0.33
Nodes (6): DecisionResponse, InteractionDataPayload, BaseModel, API Data Models. Defines the external API request and response schemas. These…, Interaction payload from the client., External response payload.

### Community 53 - ".get_safety_context"
Cohesion: 0.29
Nodes (5): SafetyContext, Session, UUID, Fetch safety context (self-exclusion, restrictions, harm indicators)., Fetch session metadata.

## Knowledge Gaps
- **90 isolated node(s):** `dwellTimer`, `sessionId`, `telemetry`, `confidence-layer`, `For /graphify add and --watch` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 342 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InteractionContext` connect `DecisionEngine` to `conftest.py`, `domain/__init__.py`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `StateEstimate` connect `StateEstimate` to `ActionId`, `UncertaintyState`, `conftest.py`, `test_domain.py`, `SafetyContract`, `DecisionContext`, `domain/__init__.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `DecisionEngine` connect `DecisionEngine` to `ContextBuilder`, `dependencies.py`, `engine.py`, `DummySafetyProvider`, `PersistenceProvider`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `DecisionEngine` (e.g. with `create_decision()` and `ContextBuilder`) actually correct?**
  _`DecisionEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `DecisionRequest` (e.g. with `create_decision()` and `DecisionEngine`) actually correct?**
  _`DecisionRequest` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `StateEstimate` (e.g. with `UncertaintyState` and `.test_audit_contains_full_provenance()`) actually correct?**
  _`StateEstimate` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 8 INFERRED edges - model-reasoned connections that need verification._