# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 93 files · ~48,758 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 900 nodes · 1433 edges · 107 communities (46 shown, 44 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 143 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1910de55`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SafetyContract
- ActionRegistry
- DatabasePersistenceProvider
- asyncio
- StateEstimate
- conftest.py
- connection.py
- TestSchemaCreation
- datetime
- test_domain.py
- Interactive UI & Client Telemetry
- actions.py
- Package Init (Confidence)
- Confidence Layer Root
- What You Must Do When Invoked
- What You Must Do When Invoked
- CircuitBreaker
- dependencies.py
- EventPublisher
- ActionRegistry
- test_background_audit_logger
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
- ContextBuilder
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
- ActionId
- RedisSessionStore
- event_consumer.py
- UncertaintyState
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
- ports.py
- PersistenceProvider
- get_engine
- DecisionContext
- SafetyBlockReason
- BaseModel
- datetime
- ConfidenceEvent
- DecisionEngine
- SafetyContext
- UUID
- tracing.py
- observability/__init__.py

## God Nodes (most connected - your core abstractions)
1. `SafetyContract` - 51 edges
2. `ActionId` - 28 edges
3. `ActionRegistry` - 25 edges
4. `UncertaintyState` - 21 edges
5. `ActionDefinition` - 20 edges
6. `load_config()` - 19 edges
7. `ConfidenceEvent` - 17 edges
8. `HarmIndicators` - 16 edges
9. `PolicySelector` - 13 edges
10. `NoInterventionReason` - 13 edges

## Surprising Connections (you probably didn't know these)
- `engine()` --uses--> `SafetyContract`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/safety.py
- `engine()` --calls--> `ActionRegistry`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/actions.py
- `engine()` --calls--> `ResponseGenerator`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/response.py
- `engine()` --calls--> `StateEstimator`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/state.py
- `test_policy_respects_safety_class()` --uses--> `ActionId`  [INFERRED]
  tests/test_policy.py → src/confidence/domain/enums.py

## Import Cycles
- None detected.

## Communities (107 total, 44 thin omitted)

### Community 0 - "SafetyContract"
Cohesion: 0.06
Nodes (29): Check if state estimation confidence is sufficient. S4: Unknown safety state →…, Check if user is legitimately reconsidering. The system must never assume…, Return True if an action is conversion-oriented. NO_INTERVENTION and…, Executable safety contract encoding invariants S1–S17. This contract is the…, SafetyContract, StateEstimate, datetime, SafetyContext (+21 more)

### Community 1 - "ActionRegistry"
Cohesion: 0.18
Nodes (12): DecisionContext, ActionRegistry, In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, PolicySelector, Deterministic policy selector. Selects an action based on explicit…, Generates the safe response string., ResponseGenerator, TestPolicySelector (+4 more)

### Community 2 - "DatabasePersistenceProvider"
Cohesion: 0.25
Nodes (6): DatabasePersistenceProvider, AsyncEngine, Decision, DecisionContext, Saves decisions and audit records asynchronously to the database. All column…, Persist a decision and its audit log to the database. Called as a background…

### Community 3 - "asyncio"
Cohesion: 0.07
Nodes (36): asyncio, ContextBuilder, DecisionEngine, DecisionRequest, fixture, MarketContext, MarketProvider, SafetyProvider (+28 more)

### Community 4 - "StateEstimate"
Cohesion: 0.15
Nodes (11): DecisionContext, Complete context assembled by the Context Builder for a decision. This is the…, Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, Select the best action from the eligible set., State Authority. Classifies user uncertainty during betslip confirmation into a…, Deterministic rule-based state estimator. Evaluates the decision context and…, Evaluate context and return the highest priority state estimate. (+3 more)

### Community 5 - "conftest.py"
Cohesion: 0.06
Nodes (51): SlipContext, HarmIndicators, MarketContext, OddsSnapshot, BaseModel, Safety-relevant state, sourced from authoritative server-side systems. These…, A user's betslip confirmation session., A point-in-time odds value from an authoritative source. (+43 more)

### Community 6 - "connection.py"
Cohesion: 0.15
Nodes (16): async_sessionmaker, AsyncSession, Engine, sessionmaker, DatabaseConfig, PostgreSQL connection configuration., create_async_db_engine(), create_async_session_factory() (+8 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "datetime"
Cohesion: 0.11
Nodes (16): BaseModel, datetime, field_validator, SafetyContext, SafetyResult, EventType, Types of client events the system processes., ConfidenceEvent (+8 more)

### Community 9 - "test_domain.py"
Cohesion: 0.09
Nodes (16): Output of the Safety Authority. The Safety Authority answers: 'Can we…, SafetyResult, datetime, DecisionContext, Session, SlipContext, Tests for domain model validation. Verifies that all Pydantic domain models…, TestAuditRecord (+8 more)

### Community 10 - "Interactive UI & Client Telemetry"
Cohesion: 0.22
Nodes (5): dwellTimer, evaluateDecision(), sessionId, telemetry, updatePipeline()

### Community 11 - "actions.py"
Cohesion: 0.29
Nodes (5): Versioned Action Registry for the Confidence Layer. The Action Registry is the…, ActionCategory, Semantic categories for actions., Policy Authority. Selects the best action from a set of safe and eligible…, Response Generator. Deterministically formats the final response using approved…

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 19 - "CircuitBreaker"
Cohesion: 0.22
Nodes (4): CircuitBreaker, A simple async circuit breaker., Record a success and reset if half-open., Check if execution is allowed.

### Community 20 - "dependencies.py"
Cohesion: 0.21
Nodes (13): ActionRegistry, PolicySelector, ResponseGenerator, SafetyContract, get_action_registry(), get_decision_engine(), get_policy_selector(), get_response_generator() (+5 more)

### Community 21 - "EventPublisher"
Cohesion: 0.10
Nodes (11): EventPublisher, InMemoryEventPublisher, KafkaEventPublisher, ConfidenceEvent, Event Bus Abstraction. Provides a unified interface for publishing events to…, Interface for publishing events., Publish a domain event to the message broker., Kafka/Redpanda implementation of the event publisher. (+3 more)

### Community 22 - "ActionRegistry"
Cohesion: 0.11
Nodes (10): ActionRegistry, Tests for the Action Registry. Verifies: - All 6 initial actions are registered…, When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be…, Disabled actions should not appear in eligible lists., NO_INTERVENTION must be eligible for every possible state., When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible., TestActionDefinitions, TestActionEligibility (+2 more)

### Community 23 - "test_background_audit_logger"
Cohesion: 0.10
Nodes (14): AuditStore, BackgroundAuditLogger, KafkaAuditStore, AuditRecord, Audit Trail. Persists full audit records for every decision. Audit persistence…, Interface for audit persistence., Save an audit record., Publishes audit records to Kafka for downstream data warehousing. (+6 more)

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

### Community 37 - "ContextBuilder"
Cohesion: 0.18
Nodes (13): ContextBuilder, Context Builder. Constructs the DecisionContext from the incoming request and…, Builds a complete, trustworthy DecisionContext., Construct the context safely., execute_with_resilience(), Resilience patterns. Implements timeouts, circuit breakers, and retries for…, Configuration for resilience strategies., Execute a function with timeout, retries, and circuit breaker. (+5 more)

### Community 49 - "domain/models.py"
Cohesion: 0.13
Nodes (23): NoInterventionReason, OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Types of outcomes following a decision., Safety classification of an action., Result of the Safety Authority's evaluation. SAFE: intervention is permitted.…, Return True if this status forces a fail-closed response., Why the Safety Authority blocked an intervention. (+15 more)

### Community 52 - "RedisSessionStore"
Cohesion: 0.10
Nodes (19): Any, InteractionContext, Session, Redis, UUID, Session State & Idempotency in Redis. Manages distributed state for sessions…, Attempt to acquire idempotency lock. Returns True if acquired (first attempt)., Save the successful response for a given idempotency key. (+11 more)

### Community 53 - "event_consumer.py"
Cohesion: 0.18
Nodes (9): RedisSessionStore, EventProcessor, ConfidenceEvent, Event Processor. Processes incoming events from the message broker to update…, Processes domain events to update interaction context., Process a single event and update the session., Event Consumer Worker. Long-running process that consumes events from…, Run the event consumer loop. (+1 more)

### Community 54 - "UncertaintyState"
Cohesion: 0.19
Nodes (11): CreateDecisionRequest, DecisionResponse, InteractionDataPayload, BaseModel, API Data Models. Defines the external API request and response schemas. These…, Interaction payload from the client., External request payload for a new decision., External response payload. (+3 more)

### Community 55 - "ActionId"
Cohesion: 0.14
Nodes (10): ActionDefinition, Return all registered action IDs., Definition of a single registered action. Each action declares: - which…, Get an action definition by ID., Check if an action is registered (invariant S9)., Return all currently enabled actions., ActionId, Registered action identifiers. The policy can only select from these registered… (+2 more)

### Community 56 - "create_decision"
Cohesion: 0.12
Nodes (18): ConfidenceEvent, CreateDecisionRequest, DecisionResponse, EventPublisher, get, JSONResponse, post, RedisIdempotencyStore (+10 more)

### Community 57 - "DecisionRequest"
Cohesion: 0.17
Nodes (14): NoInterventionReason, DecisionRequest, The incoming API request for a decision., DecisionEngine, DecisionResult, Decision, DecisionContext, The core orchestration logic. (+6 more)

### Community 69 - "SequenceValidator"
Cohesion: 0.27
Nodes (6): Redis, UUID, Event Ordering. Validates sequence numbers to enforce strict ordering of events…, Validates and tracks event sequence numbers using Redis., Validate that the sequence number is exactly the next expected one. If valid,…, SequenceValidator

### Community 70 - "app.py"
Cohesion: 0.25
Nodes (10): FastAPI, create_app(), lifespan(), FastAPI application entrypoint. Uses the modern lifespan context manager for…, Application lifespan manager — handles startup and shutdown., Create and configure the FastAPI application., get_event_publisher(), Get the event publisher instance. (+2 more)

### Community 84 - "ports.py"
Cohesion: 0.10
Nodes (19): Protocol, MarketProvider, MarketContext, SafetyContext, Session, SlipContext, UUID, Domain Ports (Protocols). The domain owns its interfaces (hexagonal… (+11 more)

### Community 85 - "PersistenceProvider"
Cohesion: 0.17
Nodes (10): ActionRegistry, PolicySelector, ResponseGenerator, SafetyContract, StateEstimator, PersistenceProvider, Decision, DecisionContext (+2 more)

### Community 86 - "get_engine"
Cohesion: 0.29
Nodes (6): AsyncEngine, PersistenceProvider, get_engine(), get_persistence_provider(), Get or create the async database engine., DummyPersistenceProvider

### Community 97 - "UUID"
Cohesion: 0.11
Nodes (14): Decision Engine Orchestrator. Coordinates the complete end-to-end pipeline: 1.…, DeadLetterQueue, KafkaDeadLetterQueue, Protocol, Dead Letter Queue (DLQ). Handles events that fail processing or validation., Interface for dead-lettering failed events., Push a failed message to the DLQ., Kafka/Redpanda implementation of DLQ. (+6 more)

### Community 101 - "tracing.py"
Cohesion: 0.33
Nodes (5): get_tracer(), OpenTelemetry tracing setup., Initialize OpenTelemetry tracing., setup_tracing(), Tracer

## Knowledge Gaps
- **90 isolated node(s):** `dwellTimer`, `sessionId`, `telemetry`, `confidence-layer`, `For /graphify add and --watch` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 450 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SafetyContract` connect `SafetyContract` to `asyncio`, `conftest.py`, `datetime`, `domain/models.py`, `UncertaintyState`, `ActionId`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `engine()` connect `asyncio` to `SafetyContract`, `ActionRegistry`, `StateEstimate`, `ContextBuilder`, `get_engine`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `ActionDefinition` connect `ActionId` to `SafetyContract`, `ActionRegistry`, `StateEstimate`, `datetime`, `actions.py`, `domain/models.py`, `UncertaintyState`, `ActionRegistry`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `SafetyContract` (e.g. with `ActionDefinition` and `ActionId`) actually correct?**
  _`SafetyContract` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ActionRegistry` (e.g. with `ActionId` and `UncertaintyState`) actually correct?**
  _`ActionRegistry` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `UncertaintyState` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`UncertaintyState` has 10 INFERRED edges - model-reasoned connections that need verification._