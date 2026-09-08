# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 75 files · ~45,757 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 816 nodes · 1304 edges · 96 communities (49 shown, 40 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 112 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c62a3470`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StateEstimate
- ActionId
- UUID
- DecisionRequest
- DecisionContext
- conftest.py
- connection.py
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
- EventPublisher
- ActionRegistry
- enums.py
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- DummyMarketProvider
- load_config
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
- domain/models.py
- Protocol
- DecisionContext
- RedisSessionStore
- event_consumer.py
- SafetyStatus
- ActionDefinition
- create_decision
- ._build_failure_decision
- ActionRegistry
- AsyncEngine
- MarketContext
- ContextBuilder
- BaseModel
- ContextBuilder
- Protocol
- UUID
- fixture
- PolicySelector
- SequenceValidator
- log.py
- BaseModel
- datetime
- ResponseGenerator
- SafetyContext
- SafetyContract
- SlipContext
- StateEstimator
- UUID
- Protocol
- KafkaDeadLetterQueue
- test_session_state.py
- test_engine.py
- .get_safety_context
- .__init__
- DummySafetyProvider
- .persist_decision
- .build
- .get_market_context
- .get_slip_context
- .test_prohibited_copy
- ConfidenceEvent
- DecisionEngine

## God Nodes (most connected - your core abstractions)
1. `StateEstimate` - 28 edges
2. `DecisionRequest` - 28 edges
3. `DecisionEngine` - 28 edges
4. `ActionId` - 26 edges
5. `UncertaintyState` - 19 edges
6. `load_config()` - 19 edges
7. `ConfidenceEvent` - 17 edges
8. `SafetyContract` - 16 edges
9. `HarmIndicators` - 16 edges
10. `ActionDefinition` - 16 edges

## Surprising Connections (you probably didn't know these)
- `engine()` --uses--> `ContextBuilder`  [INFERRED]
  tests/test_engine.py → src/confidence/application/context_builder.py
- `test_in_memory_event_publisher()` --uses--> `InMemoryEventPublisher`  [INFERRED]
  tests/test_event_bus.py → src/confidence/infrastructure/event_bus.py
- `engine()` --uses--> `DummyMarketProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `engine()` --uses--> `DummySafetyProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestAdversarialAndFailures` --uses--> `DummySafetyProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py

## Import Cycles
- None detected.

## Communities (96 total, 40 thin omitted)

### Community 0 - "StateEstimate"
Cohesion: 0.08
Nodes (25): Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, TestStateEstimate, datetime, SafetyContext, SafetyContract, Tests for the Safety Contract. Verifies all 17 system invariants (S1–S17) as…, S4: Unknown safety state → fail closed. (+17 more)

### Community 1 - "ActionId"
Cohesion: 0.16
Nodes (11): ActionRegistry, Return all registered action IDs., In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Get an action definition by ID., Check if an action is registered (invariant S9)., ActionId, Registered action identifiers. The policy can only select from these registered…, Response Generator. Deterministically formats the final response using approved… (+3 more)

### Community 2 - "UUID"
Cohesion: 0.13
Nodes (21): Protocol, ContextBuilder, Context Builder. Constructs the DecisionContext from the incoming request and…, Builds a complete, trustworthy DecisionContext., Decision Engine Orchestrator. Coordinates the complete end-to-end pipeline: 1.…, MarketProvider, PersistenceProvider, Domain Ports (Protocols). The domain owns its interfaces (hexagonal… (+13 more)

### Community 3 - "DecisionRequest"
Cohesion: 0.22
Nodes (11): asyncio, DecisionRequest, The incoming API request for a decision., DecisionEngine, Central orchestrator for the Confidence Layer. Executes the decision pipeline…, ∀ blocked safety contexts: selected_action == NO_INTERVENTION, ∀ selected actions: selected_action ∈ ActionRegistry, ∀ selected informational actions: required_data ⊆ available_authoritative_data (+3 more)

### Community 4 - "DecisionContext"
Cohesion: 0.29
Nodes (6): DecisionContext, Complete context assembled by the Context Builder for a decision. This is the…, State Authority. Classifies user uncertainty during betslip confirmation into a…, Deterministic rule-based state estimator. Evaluates the decision context and…, Evaluate context and return the highest priority state estimate., StateEstimator

### Community 5 - "conftest.py"
Cohesion: 0.06
Nodes (54): SlipContext, HarmIndicators, InteractionContext, MarketContext, OddsSnapshot, Outcome, BaseModel, Safety-relevant state, sourced from authoritative server-side systems. These… (+46 more)

### Community 6 - "connection.py"
Cohesion: 0.15
Nodes (14): async_sessionmaker, AsyncSession, Engine, sessionmaker, create_async_db_engine(), create_async_session_factory(), create_sync_db_engine(), create_sync_session_factory() (+6 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "ConfidenceEvent"
Cohesion: 0.14
Nodes (13): BaseModel, datetime, field_validator, EventType, Types of client events the system processes., ConfidenceEvent, Versioned event schema for the Confidence Layer. Events are the primary input…, A versioned event from the client. Schema follows the architecture spec's event… (+5 more)

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
Cohesion: 0.12
Nodes (23): ActionRegistry, AsyncEngine, ContextBuilder, PersistenceProvider, PolicySelector, ResponseGenerator, SafetyContract, SlipProvider (+15 more)

### Community 21 - "EventPublisher"
Cohesion: 0.10
Nodes (11): EventPublisher, InMemoryEventPublisher, KafkaEventPublisher, ConfidenceEvent, Event Bus Abstraction. Provides a unified interface for publishing events to…, Interface for publishing events., Publish a domain event to the message broker., Kafka/Redpanda implementation of the event publisher. (+3 more)

### Community 22 - "ActionRegistry"
Cohesion: 0.11
Nodes (10): ActionRegistry, Tests for the Action Registry. Verifies: - All 6 initial actions are registered…, When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be…, Disabled actions should not appear in eligible lists., NO_INTERVENTION must be eligible for every possible state., When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible., TestActionDefinitions, TestActionEligibility (+2 more)

### Community 23 - "enums.py"
Cohesion: 0.24
Nodes (11): Versioned Action Registry for the Confidence Layer. The Action Registry is the…, ActionCategory, OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Possible states of user uncertainty during betslip confirmation. The State…, Types of outcomes following a decision., Semantic categories for actions., UncertaintyState (+3 more)

### Community 24 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 25 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 26 - "DummyMarketProvider"
Cohesion: 0.40
Nodes (4): MarketContext, MarketProvider, DummyMarketProvider, Synthetic market provider for demo scenarios.

### Community 27 - "load_config"
Cohesion: 0.16
Nodes (17): AppConfig, DatabaseConfig, DecisionConfig, KafkaConfig, load_config(), _load_env(), Environment-based configuration for the Confidence Layer. All configuration is…, Load .env file if present. (+9 more)

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

### Community 49 - "domain/models.py"
Cohesion: 0.13
Nodes (16): NoInterventionReason, Why the Safety Authority blocked an intervention., Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no…, SafetyBlockReason, AuditRecord, Decision, Strongly typed domain models for the Confidence Layer. All version-sensitive…, A complete decision record with full provenance. Must be reproducible from its… (+8 more)

### Community 51 - "DecisionContext"
Cohesion: 0.22
Nodes (5): DecisionContext, Harm > everything else., TestPolicySelector, TestResponseGenerator, TestStateEstimator

### Community 52 - "RedisSessionStore"
Cohesion: 0.11
Nodes (17): Any, InteractionContext, Session, Redis, UUID, Session State & Idempotency in Redis. Manages distributed state for sessions…, Attempt to acquire idempotency lock. Returns True if acquired (first attempt)., Save the successful response for a given idempotency key. (+9 more)

### Community 53 - "event_consumer.py"
Cohesion: 0.18
Nodes (9): RedisSessionStore, EventProcessor, ConfidenceEvent, Event Processor. Processes incoming events from the message broker to update…, Processes domain events to update interaction context., Process a single event and update the session., Event Consumer Worker. Long-running process that consumes events from…, Run the event consumer loop. (+1 more)

### Community 54 - "SafetyStatus"
Cohesion: 0.19
Nodes (11): CreateDecisionRequest, DecisionResponse, InteractionDataPayload, BaseModel, API Data Models. Defines the external API request and response schemas. These…, Interaction payload from the client., External request payload for a new decision., External response payload. (+3 more)

### Community 55 - "ActionDefinition"
Cohesion: 0.17
Nodes (8): ActionDefinition, BaseModel, Definition of a single registered action. Each action declares: - which…, Return all currently enabled actions., Return actions eligible for a given state and available data. An action is…, PolicySelector, Deterministic policy selector. Selects an action based on explicit…, Select the best action from the eligible set.

### Community 56 - "create_decision"
Cohesion: 0.17
Nodes (12): ConfidenceEvent, CreateDecisionRequest, DecisionEngine, DecisionResponse, EventPublisher, JSONResponse, post, RedisIdempotencyStore (+4 more)

### Community 57 - "._build_failure_decision"
Cohesion: 0.17
Nodes (10): NoInterventionReason, DecisionResult, Decision, DecisionContext, The core orchestration logic., Compute which data keys are actually available from authoritative sources. Only…, Create a fail-closed decision for unexpected errors., The result of the decision pipeline. (+2 more)

### Community 69 - "SequenceValidator"
Cohesion: 0.27
Nodes (6): Redis, UUID, Event Ordering. Validates sequence numbers to enforce strict ordering of events…, Validates and tracks event sequence numbers using Redis., Validate that the sequence number is exactly the next expected one. If valid,…, SequenceValidator

### Community 70 - "log.py"
Cohesion: 0.16
Nodes (15): FastAPI, create_app(), lifespan(), FastAPI application entrypoint. Uses the modern lifespan context manager for…, Application lifespan manager — handles startup and shutdown., Create and configure the FastAPI application., get_event_publisher(), Get the event publisher instance. (+7 more)

### Community 81 - "KafkaDeadLetterQueue"
Cohesion: 0.13
Nodes (10): DeadLetterQueue, KafkaDeadLetterQueue, Protocol, Dead Letter Queue (DLQ). Handles events that fail processing or validation., Interface for dead-lettering failed events., Push a failed message to the DLQ., Kafka/Redpanda implementation of DLQ., Start the DLQ producer. (+2 more)

### Community 82 - "test_session_state.py"
Cohesion: 0.25
Nodes (7): Tests for session state and event ordering., Provide a FakeRedis connection., redis(), test_idempotency_store(), test_sequence_validator(), test_session_store_save_get(), test_session_store_update_interaction()

### Community 83 - "test_engine.py"
Cohesion: 0.38
Nodes (5): fixture, base_request(), DummyPersistenceProvider, engine(), Tests for the Decision Engine and End-to-End Scenarios. Covers: - Unit tests…

### Community 84 - ".get_safety_context"
Cohesion: 0.29
Nodes (5): SafetyContext, Session, UUID, Fetch safety context (self-exclusion, restrictions, harm indicators)., Fetch session metadata.

### Community 85 - ".__init__"
Cohesion: 0.33
Nodes (5): ActionRegistry, PolicySelector, ResponseGenerator, SafetyContract, StateEstimator

### Community 86 - "DummySafetyProvider"
Cohesion: 0.40
Nodes (4): SafetyContext, SafetyProvider, DummySafetyProvider, Synthetic safety provider for demo scenarios. Branches on actor_id — NEVER use…

### Community 87 - ".persist_decision"
Cohesion: 0.50
Nodes (3): Decision, DecisionContext, Persist a decision and its audit log to the database.

## Knowledge Gaps
- **90 isolated node(s):** `dwellTimer`, `sessionId`, `telemetry`, `confidence-layer`, `For /graphify add and --watch` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 411 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InteractionContext` connect `conftest.py` to `create_decision`, `domain/models.py`, `test_engine.py`, `DecisionRequest`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `StateEstimate` connect `StateEstimate` to `DecisionContext`, `conftest.py`, `test_domain.py`, `domain/models.py`, `DecisionContext`, `enums.py`, `ActionDefinition`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `HarmIndicators` connect `conftest.py` to `StateEstimate`, `domain/models.py`, `DummySafetyProvider`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `StateEstimate` (e.g. with `UncertaintyState` and `.test_audit_contains_full_provenance()`) actually correct?**
  _`StateEstimate` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `DecisionRequest` (e.g. with `create_decision()` and `DecisionEngine`) actually correct?**
  _`DecisionRequest` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `DecisionEngine` (e.g. with `ContextBuilder` and `DecisionRequest`) actually correct?**
  _`DecisionEngine` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 8 INFERRED edges - model-reasoned connections that need verification._