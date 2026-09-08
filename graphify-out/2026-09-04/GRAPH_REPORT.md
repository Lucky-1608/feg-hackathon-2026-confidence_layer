# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 70 files · ~44,751 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 771 nodes · 1266 edges · 74 communities (40 shown, 31 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 113 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7a49459f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StateEstimate
- ActionId
- ContextBuilder
- DecisionEngine
- UncertaintyState
- domain/models.py
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
- KafkaEventPublisher
- ActionRegistry
- enums.py
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- test_engine.py
- .__init__
- graphify reference: query, path, explain
- env.py
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- .persist_decision
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
- RedisSessionStore
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
- KafkaDeadLetterQueue
- SequenceValidator
- engine.py
- BaseModel
- datetime
- .persist_decision

## God Nodes (most connected - your core abstractions)
1. `DecisionEngine` - 32 edges
2. `DecisionRequest` - 29 edges
3. `StateEstimate` - 28 edges
4. `ActionId` - 26 edges
5. `UncertaintyState` - 19 edges
6. `ConfidenceEvent` - 17 edges
7. `SafetyContract` - 16 edges
8. `HarmIndicators` - 16 edges
9. `ActionDefinition` - 16 edges
10. `ActionRegistry` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_sequence_validator()` --uses--> `SequenceValidator`  [INFERRED]
  tests/test_session_state.py → src/confidence/infrastructure/event_ordering.py
- `test_session_store_save_get()` --uses--> `RedisSessionStore`  [INFERRED]
  tests/test_session_state.py → src/confidence/infrastructure/session_state.py
- `test_session_store_update_interaction()` --uses--> `RedisSessionStore`  [INFERRED]
  tests/test_session_state.py → src/confidence/infrastructure/session_state.py
- `test_idempotency_store()` --uses--> `RedisIdempotencyStore`  [INFERRED]
  tests/test_session_state.py → src/confidence/infrastructure/session_state.py
- `engine()` --uses--> `ContextBuilder`  [INFERRED]
  tests/test_engine.py → src/confidence/application/context_builder.py

## Import Cycles
- None detected.

## Communities (74 total, 31 thin omitted)

### Community 0 - "StateEstimate"
Cohesion: 0.08
Nodes (25): Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, TestStateEstimate, datetime, SafetyContext, SafetyContract, Tests for the Safety Contract. Verifies all 17 system invariants (S1–S17) as…, S4: Unknown safety state → fail closed. (+17 more)

### Community 1 - "ActionId"
Cohesion: 0.11
Nodes (18): ActionDefinition, ActionRegistry, BaseModel, Return all registered action IDs., Definition of a single registered action. Each action declares: - which…, In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Get an action definition by ID., Check if an action is registered (invariant S9). (+10 more)

### Community 2 - "ContextBuilder"
Cohesion: 0.23
Nodes (13): Protocol, ContextBuilder, Context Builder. Constructs the DecisionContext from the incoming request and…, Builds a complete, trustworthy DecisionContext., MarketProvider, Domain Ports (Protocols). The domain owns its interfaces (hexagonal…, Provides authoritative safety state for a session/user., Provides authoritative betslip state. (+5 more)

### Community 3 - "DecisionEngine"
Cohesion: 0.05
Nodes (47): asyncio, BaseModel, fixture, NoInterventionReason, post, CreateDecisionRequest, DecisionResponse, InteractionDataPayload (+39 more)

### Community 4 - "UncertaintyState"
Cohesion: 0.16
Nodes (10): Return actions eligible for a given state and available data. An action is…, Possible states of user uncertainty during betslip confirmation. The State…, UncertaintyState, DecisionContext, Complete context assembled by the Context Builder for a decision. This is the…, Generate response based on the selected action and available context., State Authority. Classifies user uncertainty during betslip confirmation into a…, Deterministic rule-based state estimator. Evaluates the decision context and… (+2 more)

### Community 5 - "domain/models.py"
Cohesion: 0.06
Nodes (55): SlipContext, AuditRecord, HarmIndicators, MarketContext, OddsSnapshot, Outcome, BaseModel, Strongly typed domain models for the Confidence Layer. All version-sensitive… (+47 more)

### Community 6 - "config.py"
Cohesion: 0.07
Nodes (37): async_sessionmaker, AsyncSession, Engine, FastAPI, sessionmaker, create_app(), lifespan(), FastAPI application entrypoint. Uses the modern lifespan context manager for… (+29 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "ConfidenceEvent"
Cohesion: 0.17
Nodes (10): datetime, field_validator, EventType, Types of client events the system processes., ConfidenceEvent, Versioned event schema for the Confidence Layer. Events are the primary input…, A versioned event from the client. Schema follows the architecture spec's event…, Tests for the event schema. Verifies event validation, required fields,… (+2 more)

### Community 9 - "test_domain.py"
Cohesion: 0.09
Nodes (17): Output of the Safety Authority. The Safety Authority answers: 'Can we…, SafetyResult, datetime, Evaluate whether intervention is permitted. Returns a SafetyResult with status…, datetime, DecisionContext, Session, SlipContext (+9 more)

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
Cohesion: 0.13
Nodes (21): get_action_registry(), get_decision_engine(), get_engine(), get_persistence_provider(), get_policy_selector(), get_response_generator(), get_safety_contract(), get_state_estimator() (+13 more)

### Community 21 - "KafkaEventPublisher"
Cohesion: 0.10
Nodes (14): ConfidenceEvent, EventPublisher, InMemoryEventPublisher, KafkaEventPublisher, Protocol, Event Bus Abstraction. Provides a unified interface for publishing events to…, Interface for publishing events., Publish a domain event to the message broker. (+6 more)

### Community 22 - "ActionRegistry"
Cohesion: 0.11
Nodes (10): ActionRegistry, Tests for the Action Registry. Verifies: - All 6 initial actions are registered…, When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be…, Disabled actions should not appear in eligible lists., NO_INTERVENTION must be eligible for every possible state., When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible., TestActionDefinitions, TestActionEligibility (+2 more)

### Community 23 - "enums.py"
Cohesion: 0.18
Nodes (12): API Data Models. Defines the external API request and response schemas. These…, Versioned Action Registry for the Confidence Layer. The Action Registry is the…, ActionCategory, OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Types of outcomes following a decision., Result of the Safety Authority's evaluation. SAFE: intervention is permitted.…, Return True if this status forces a fail-closed response. (+4 more)

### Community 24 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 25 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 26 - "test_engine.py"
Cohesion: 0.14
Nodes (13): DummyMarketProvider, DummySafetyProvider, DummySlipProvider, get_context_builder(), MarketContext, SafetyContext, UUID, Synthetic safety provider for demo scenarios. Branches on actor_id — NEVER use… (+5 more)

### Community 27 - ".__init__"
Cohesion: 0.33
Nodes (5): ActionRegistry, PolicySelector, ResponseGenerator, SafetyContract, StateEstimator

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

### Community 37 - ".persist_decision"
Cohesion: 0.50
Nodes (3): Decision, DecisionContext, Persist a decision and its audit log to the database. Called as a background…

### Community 49 - "SafetyContract"
Cohesion: 0.14
Nodes (13): NoInterventionReason, Why the Safety Authority blocked an intervention., Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no…, SafetyBlockReason, Decision, A complete decision record with full provenance. Must be reproducible from its…, Safety Contract for the Confidence Layer. Encodes system invariants S1–S17 as…, Check if state estimation confidence is sufficient. S4: Unknown safety state →… (+5 more)

### Community 51 - "DecisionContext"
Cohesion: 0.22
Nodes (5): DecisionContext, Harm > everything else., TestPolicySelector, TestResponseGenerator, TestStateEstimator

### Community 52 - "RedisSessionStore"
Cohesion: 0.10
Nodes (19): Any, InteractionContext, Session, Redis, UUID, Session State & Idempotency in Redis. Manages distributed state for sessions…, Attempt to acquire idempotency lock. Returns True if acquired (first attempt)., Save the successful response for a given idempotency key. (+11 more)

### Community 53 - ".get_safety_context"
Cohesion: 0.29
Nodes (5): SafetyContext, Session, UUID, Fetch safety context (self-exclusion, restrictions, harm indicators)., Fetch session metadata.

### Community 68 - "KafkaDeadLetterQueue"
Cohesion: 0.14
Nodes (9): DeadLetterQueue, KafkaDeadLetterQueue, Protocol, Interface for dead-lettering failed events., Push a failed message to the DLQ., Kafka/Redpanda implementation of DLQ., Start the DLQ producer., Stop the DLQ producer. (+1 more)

### Community 69 - "SequenceValidator"
Cohesion: 0.27
Nodes (6): Redis, UUID, Event Ordering. Validates sequence numbers to enforce strict ordering of events…, Validates and tracks event sequence numbers using Redis., Validate that the sequence number is exactly the next expected one. If valid,…, SequenceValidator

### Community 70 - "engine.py"
Cohesion: 0.28
Nodes (5): Decision Engine Orchestrator. Coordinates the complete end-to-end pipeline: 1.…, Dead Letter Queue (DLQ). Handles events that fail processing or validation., Persistence for audit logs and decisions. Architectural constraint: Persistence…, Structured logging for the Confidence Layer. Uses structlog for JSON-formatted,…, UUID

### Community 73 - ".persist_decision"
Cohesion: 0.50
Nodes (3): Decision, DecisionContext, Persist a decision and its audit log to the database.

## Knowledge Gaps
- **90 isolated node(s):** `confidence-layer`, `dwellTimer`, `sessionId`, `telemetry`, `For /graphify add and --watch` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 379 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StateEstimate` connect `StateEstimate` to `ActionId`, `UncertaintyState`, `domain/models.py`, `test_domain.py`, `SafetyContract`, `DecisionContext`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `ActionId` connect `ActionId` to `DecisionEngine`, `UncertaintyState`, `domain/models.py`, `.is_conversion_oriented`, `SafetyContract`, `enums.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `InteractionContext` connect `DecisionEngine` to `domain/models.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `DecisionEngine` (e.g. with `create_decision()` and `ContextBuilder`) actually correct?**
  _`DecisionEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `DecisionRequest` (e.g. with `create_decision()` and `DecisionEngine`) actually correct?**
  _`DecisionRequest` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `StateEstimate` (e.g. with `UncertaintyState` and `.test_audit_contains_full_provenance()`) actually correct?**
  _`StateEstimate` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 8 INFERRED edges - model-reasoned connections that need verification._