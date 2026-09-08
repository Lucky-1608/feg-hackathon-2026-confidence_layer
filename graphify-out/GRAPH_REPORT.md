# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 79 files · ~46,471 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 845 nodes · 1329 edges · 91 communities (45 shown, 38 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 117 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `786b2f5a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SafetyContract
- ActionRegistry
- log.py
- asyncio
- UncertaintyState
- conftest.py
- connection.py
- TestSchemaCreation
- ConfidenceEvent
- test_domain.py
- Interactive UI & Client Telemetry
- UUID
- Package Init (Confidence)
- Confidence Layer Root
- What You Must Do When Invoked
- What You Must Do When Invoked
- BaseModel
- dependencies.py
- EventPublisher
- ActionRegistry
- DatabasePersistenceProvider
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
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
- execute_with_resilience
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
- api/models.py
- ActionId
- create_decision
- DecisionRequest
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
- app.py
- BaseModel
- datetime
- ResponseGenerator
- SafetyContext
- SafetyContract
- SlipContext
- StateEstimator
- UUID
- Protocol
- DecisionContext
- SafetyContract
- Protocol
- ContextBuilder
- DummyMarketProvider
- DecisionContext
- ConfidenceEvent
- DecisionEngine

## God Nodes (most connected - your core abstractions)
1. `SafetyContract` - 44 edges
2. `ActionRegistry` - 23 edges
3. `ActionId` - 22 edges
4. `load_config()` - 19 edges
5. `UncertaintyState` - 17 edges
6. `ConfidenceEvent` - 17 edges
7. `HarmIndicators` - 16 edges
8. `ActionDefinition` - 16 edges
9. `engine()` - 13 edges
10. `TestSchemaCreation` - 13 edges

## Surprising Connections (you probably didn't know these)
- `engine()` --uses--> `SafetyContract`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/safety.py
- `engine()` --calls--> `DummyMarketProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `engine()` --calls--> `DummySafetyProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `engine()` --calls--> `DummySlipProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `engine()` --calls--> `ContextBuilder`  [INFERRED]
  tests/test_engine.py → src/confidence/application/context_builder.py

## Import Cycles
- None detected.

## Communities (91 total, 38 thin omitted)

### Community 0 - "SafetyContract"
Cohesion: 0.05
Nodes (39): ActionId, NoInterventionReason, SafetyBlockReason, SafetyResult, datetime, SafetyContext, Safety Contract for the Confidence Layer. Encodes system invariants S1–S17 as…, Check if state estimation confidence is sufficient. S4: Unknown safety state →… (+31 more)

### Community 1 - "ActionRegistry"
Cohesion: 0.14
Nodes (11): ActionRegistry, Return all registered action IDs., In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Check if an action is registered (invariant S9)., Return all currently enabled actions., OddsSnapshot, A point-in-time odds value from an authoritative source., Response Generator. Deterministically formats the final response using approved… (+3 more)

### Community 2 - "log.py"
Cohesion: 0.18
Nodes (9): Decision Engine Orchestrator. Coordinates the complete end-to-end pipeline: 1.…, PersistenceProvider, Decision, DecisionContext, Domain Ports (Protocols). The domain owns its interfaces (hexagonal…, Interface for async audit logging., Persist a decision and its audit log to the database., Persistence for audit logs and decisions. Architectural constraint: Persistence… (+1 more)

### Community 3 - "asyncio"
Cohesion: 0.09
Nodes (24): asyncio, DecisionEngine, DecisionRequest, fixture, InteractionContext, Behavioral signals from the user's interaction with the betslip. Every feature…, base_request(), DummyPersistenceProvider (+16 more)

### Community 4 - "UncertaintyState"
Cohesion: 0.16
Nodes (10): Return actions eligible for a given state and available data. An action is…, Possible states of user uncertainty during betslip confirmation. The State…, UncertaintyState, DecisionContext, Complete context assembled by the Context Builder for a decision. This is the…, Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, Generate response based on the selected action and available context. (+2 more)

### Community 5 - "conftest.py"
Cohesion: 0.08
Nodes (40): SafetyContext, HarmIndicators, MarketContext, Safety-relevant state, sourced from authoritative server-side systems. These…, Authoritative market data for a selection., Behavioral indicators of potential gambling harm. These are derived from…, Return True if any harm indicator is present., SafetyContext (+32 more)

### Community 6 - "connection.py"
Cohesion: 0.15
Nodes (16): async_sessionmaker, AsyncSession, Engine, sessionmaker, DatabaseConfig, PostgreSQL connection configuration., create_async_db_engine(), create_async_session_factory() (+8 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "ConfidenceEvent"
Cohesion: 0.17
Nodes (10): datetime, field_validator, EventType, Types of client events the system processes., ConfidenceEvent, Versioned event schema for the Confidence Layer. Events are the primary input…, A versioned event from the client. Schema follows the architecture spec's event…, Tests for the event schema. Verifies event validation, required fields,… (+2 more)

### Community 9 - "test_domain.py"
Cohesion: 0.07
Nodes (18): SlipContext, A single selection within a betslip., Selection, datetime, DecisionContext, Session, SlipContext, Tests for domain model validation. Verifies that all Pydantic domain models… (+10 more)

### Community 10 - "Interactive UI & Client Telemetry"
Cohesion: 0.22
Nodes (5): dwellTimer, evaluateDecision(), sessionId, telemetry, updatePipeline()

### Community 11 - "UUID"
Cohesion: 0.12
Nodes (13): DeadLetterQueue, KafkaDeadLetterQueue, Protocol, Dead Letter Queue (DLQ). Handles events that fail processing or validation., Interface for dead-lettering failed events., Push a failed message to the DLQ., Kafka/Redpanda implementation of DLQ., Start the DLQ producer. (+5 more)

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 19 - "BaseModel"
Cohesion: 0.25
Nodes (8): Construct the context safely., Outcome, BaseModel, Recorded outcome following a decision. Outcomes are submitted via POST…, A user's betslip confirmation session., State of the betslip at decision time., Session, SlipContext

### Community 20 - "dependencies.py"
Cohesion: 0.15
Nodes (18): ActionRegistry, AsyncEngine, PersistenceProvider, PolicySelector, ResponseGenerator, SafetyContract, get_action_registry(), get_decision_engine() (+10 more)

### Community 21 - "EventPublisher"
Cohesion: 0.10
Nodes (11): EventPublisher, InMemoryEventPublisher, KafkaEventPublisher, ConfidenceEvent, Event Bus Abstraction. Provides a unified interface for publishing events to…, Interface for publishing events., Publish a domain event to the message broker., Kafka/Redpanda implementation of the event publisher. (+3 more)

### Community 22 - "ActionRegistry"
Cohesion: 0.11
Nodes (10): ActionRegistry, Tests for the Action Registry. Verifies: - All 6 initial actions are registered…, When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be…, Disabled actions should not appear in eligible lists., NO_INTERVENTION must be eligible for every possible state., When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible., TestActionDefinitions, TestActionEligibility (+2 more)

### Community 23 - "DatabasePersistenceProvider"
Cohesion: 0.25
Nodes (6): DatabasePersistenceProvider, AsyncEngine, Decision, DecisionContext, Saves decisions and audit records asynchronously to the database. All column…, Persist a decision and its audit log to the database. Called as a background…

### Community 24 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 25 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 27 - "load_config"
Cohesion: 0.18
Nodes (15): AppConfig, DecisionConfig, KafkaConfig, load_config(), _load_env(), Environment-based configuration for the Confidence Layer. All configuration is…, Load .env file if present., Safety Authority configuration. (+7 more)

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

### Community 37 - "execute_with_resilience"
Cohesion: 0.12
Nodes (14): CircuitBreaker, execute_with_resilience(), Resilience patterns. Implements timeouts, circuit breakers, and retries for…, A simple async circuit breaker., Record a success and reset if half-open., Check if execution is allowed., Configuration for resilience strategies., Execute a function with timeout, retries, and circuit breaker. (+6 more)

### Community 49 - "domain/models.py"
Cohesion: 0.15
Nodes (19): NoInterventionReason, OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Types of outcomes following a decision., Result of the Safety Authority's evaluation. SAFE: intervention is permitted.…, Return True if this status forces a fail-closed response., Why the Safety Authority blocked an intervention., Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no… (+11 more)

### Community 51 - "DecisionContext"
Cohesion: 0.27
Nodes (6): DecisionContext, Deterministic rule-based state estimator. Evaluates the decision context and…, StateEstimator, Harm > everything else., TestPolicySelector, TestStateEstimator

### Community 52 - "RedisSessionStore"
Cohesion: 0.10
Nodes (19): Any, InteractionContext, Session, Redis, UUID, Session State & Idempotency in Redis. Manages distributed state for sessions…, Attempt to acquire idempotency lock. Returns True if acquired (first attempt)., Save the successful response for a given idempotency key. (+11 more)

### Community 53 - "event_consumer.py"
Cohesion: 0.18
Nodes (9): RedisSessionStore, EventProcessor, ConfidenceEvent, Event Processor. Processes incoming events from the message broker to update…, Processes domain events to update interaction context., Process a single event and update the session., Event Consumer Worker. Long-running process that consumes events from…, Run the event consumer loop. (+1 more)

### Community 54 - "api/models.py"
Cohesion: 0.28
Nodes (8): CreateDecisionRequest, DecisionResponse, InteractionDataPayload, BaseModel, API Data Models. Defines the external API request and response schemas. These…, Interaction payload from the client., External request payload for a new decision., External response payload.

### Community 55 - "ActionId"
Cohesion: 0.18
Nodes (13): ActionDefinition, BaseModel, Versioned Action Registry for the Confidence Layer. The Action Registry is the…, Definition of a single registered action. Each action declares: - which…, Get an action definition by ID., ActionCategory, ActionId, Registered action identifiers. The policy can only select from these registered… (+5 more)

### Community 56 - "create_decision"
Cohesion: 0.16
Nodes (13): ConfidenceEvent, CreateDecisionRequest, DecisionResponse, EventPublisher, JSONResponse, post, RedisIdempotencyStore, Request (+5 more)

### Community 57 - "DecisionRequest"
Cohesion: 0.17
Nodes (14): BaseModel, DecisionRequest, The incoming API request for a decision., DecisionEngine, DecisionResult, Decision, DecisionContext, The core orchestration logic. (+6 more)

### Community 69 - "SequenceValidator"
Cohesion: 0.27
Nodes (6): Redis, UUID, Event Ordering. Validates sequence numbers to enforce strict ordering of events…, Validates and tracks event sequence numbers using Redis., Validate that the sequence number is exactly the next expected one. If valid,…, SequenceValidator

### Community 70 - "app.py"
Cohesion: 0.25
Nodes (10): FastAPI, create_app(), lifespan(), FastAPI application entrypoint. Uses the modern lifespan context manager for…, Application lifespan manager — handles startup and shutdown., Create and configure the FastAPI application., get_event_publisher(), Get the event publisher instance. (+2 more)

### Community 84 - "Protocol"
Cohesion: 0.10
Nodes (18): Protocol, MarketProvider, MarketContext, SafetyContext, Session, SlipContext, UUID, Provides authoritative safety state for a session/user. (+10 more)

### Community 85 - "ContextBuilder"
Cohesion: 0.20
Nodes (8): ContextBuilder, Context Builder. Constructs the DecisionContext from the incoming request and…, Builds a complete, trustworthy DecisionContext., ActionRegistry, PolicySelector, ResponseGenerator, SafetyContract, StateEstimator

### Community 86 - "DummyMarketProvider"
Cohesion: 0.16
Nodes (12): ContextBuilder, MarketContext, MarketProvider, SafetyProvider, SlipProvider, DummyMarketProvider, DummySafetyProvider, DummySlipProvider (+4 more)

## Knowledge Gaps
- **90 isolated node(s):** `dwellTimer`, `sessionId`, `telemetry`, `confidence-layer`, `For /graphify add and --watch` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 419 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `engine()` connect `asyncio` to `SafetyContract`, `ActionRegistry`, `DecisionContext`, `ContextBuilder`, `DummyMarketProvider`, `ActionId`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `SafetyContract` connect `SafetyContract` to `asyncio`, `conftest.py`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `ActionDefinition` connect `ActionId` to `ActionRegistry`, `UncertaintyState`, `ActionRegistry`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SafetyContract` (e.g. with `engine()` and `TestConversionOrientation`) actually correct?**
  _`SafetyContract` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ActionRegistry` (e.g. with `ActionId` and `UncertaintyState`) actually correct?**
  _`ActionRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `dwellTimer`, `sessionId`, `telemetry` to the rest of the system?**
  _90 weakly-connected nodes found - possible documentation gaps or missing edges._