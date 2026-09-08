# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 74 files · ~45,539 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 810 nodes · 1300 edges · 81 communities (41 shown, 35 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `60e13bf4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StateEstimate
- ActionId
- ContextBuilder
- DecisionRequest
- domain/models.py
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
- persistence.py
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
- event_consumer.py
- SafetyStatus
- ActionDefinition
- create_decision
- ConfidenceEvent
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

## God Nodes (most connected - your core abstractions)
1. `StateEstimate` - 28 edges
2. `DecisionRequest` - 28 edges
3. `DecisionEngine` - 28 edges
4. `ActionId` - 26 edges
5. `UncertaintyState` - 19 edges
6. `load_config()` - 18 edges
7. `ConfidenceEvent` - 17 edges
8. `ActionDefinition` - 16 edges
9. `SafetyContract` - 16 edges
10. `HarmIndicators` - 16 edges

## Surprising Connections (you probably didn't know these)
- `engine()` --uses--> `DummyMarketProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `test_in_memory_event_publisher()` --uses--> `InMemoryEventPublisher`  [INFERRED]
  tests/test_event_bus.py → src/confidence/infrastructure/event_bus.py
- `engine()` --uses--> `ContextBuilder`  [INFERRED]
  tests/test_engine.py → src/confidence/application/context_builder.py
- `base_request()` --calls--> `InteractionContext`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/models.py
- `test_idempotency_store()` --uses--> `RedisIdempotencyStore`  [INFERRED]
  tests/test_session_state.py → src/confidence/infrastructure/session_state.py

## Import Cycles
- None detected.

## Communities (81 total, 35 thin omitted)

### Community 0 - "StateEstimate"
Cohesion: 0.08
Nodes (25): Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, TestStateEstimate, datetime, SafetyContext, SafetyContract, Tests for the Safety Contract. Verifies all 17 system invariants (S1–S17) as…, S4: Unknown safety state → fail closed. (+17 more)

### Community 1 - "ActionId"
Cohesion: 0.16
Nodes (11): ActionRegistry, Return all registered action IDs., In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Get an action definition by ID., Check if an action is registered (invariant S9)., ActionId, Registered action identifiers. The policy can only select from these registered…, Response Generator. Deterministically formats the final response using approved… (+3 more)

### Community 2 - "ContextBuilder"
Cohesion: 0.07
Nodes (29): Protocol, ContextBuilder, DecisionContext, Context Builder. Constructs the DecisionContext from the incoming request and…, Builds a complete, trustworthy DecisionContext., Construct the context safely., ActionRegistry, PolicySelector (+21 more)

### Community 3 - "DecisionRequest"
Cohesion: 0.06
Nodes (46): asyncio, fixture, NoInterventionReason, SafetyProvider, SlipProvider, DummySafetyProvider, DummySlipProvider, Synthetic safety provider for demo scenarios. Branches on actor_id — NEVER use… (+38 more)

### Community 4 - "domain/models.py"
Cohesion: 0.14
Nodes (16): Possible states of user uncertainty during betslip confirmation. The State…, UncertaintyState, AuditRecord, Decision, DecisionContext, Outcome, Strongly typed domain models for the Confidence Layer. All version-sensitive…, Complete context assembled by the Context Builder for a decision. This is the… (+8 more)

### Community 5 - "conftest.py"
Cohesion: 0.06
Nodes (52): SlipContext, HarmIndicators, InteractionContext, MarketContext, OddsSnapshot, BaseModel, Safety-relevant state, sourced from authoritative server-side systems. These…, Behavioral signals from the user's interaction with the betslip. Every feature… (+44 more)

### Community 6 - "connection.py"
Cohesion: 0.15
Nodes (16): async_sessionmaker, AsyncSession, Engine, sessionmaker, DatabaseConfig, PostgreSQL connection configuration., create_async_db_engine(), create_async_session_factory() (+8 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "ConfidenceEvent"
Cohesion: 0.07
Nodes (25): BaseModel, datetime, field_validator, SafetyContext, EventType, Types of client events the system processes., ConfidenceEvent, Versioned event schema for the Confidence Layer. Events are the primary input… (+17 more)

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
Cohesion: 0.14
Nodes (20): ActionRegistry, AsyncEngine, ContextBuilder, PersistenceProvider, PolicySelector, ResponseGenerator, SafetyContract, get_action_registry() (+12 more)

### Community 21 - "EventPublisher"
Cohesion: 0.10
Nodes (11): EventPublisher, InMemoryEventPublisher, KafkaEventPublisher, ConfidenceEvent, Event Bus Abstraction. Provides a unified interface for publishing events to…, Interface for publishing events., Publish a domain event to the message broker., Kafka/Redpanda implementation of the event publisher. (+3 more)

### Community 22 - "ActionRegistry"
Cohesion: 0.11
Nodes (10): ActionRegistry, Tests for the Action Registry. Verifies: - All 6 initial actions are registered…, When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be…, Disabled actions should not appear in eligible lists., NO_INTERVENTION must be eligible for every possible state., When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible., TestActionDefinitions, TestActionEligibility (+2 more)

### Community 23 - "enums.py"
Cohesion: 0.22
Nodes (11): Versioned Action Registry for the Confidence Layer. The Action Registry is the…, ActionCategory, OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Types of outcomes following a decision., Why the Safety Authority blocked an intervention., Semantic categories for actions., SafetyBlockReason (+3 more)

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

### Community 37 - "persistence.py"
Cohesion: 0.20
Nodes (7): DatabasePersistenceProvider, AsyncEngine, Decision, DecisionContext, Persistence for audit logs and decisions. Architectural constraint: Persistence…, Saves decisions and audit records asynchronously to the database. All column…, Persist a decision and its audit log to the database. Called as a background…

### Community 49 - "SafetyContract"
Cohesion: 0.19
Nodes (8): NoInterventionReason, Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no…, Check if state estimation confidence is sufficient. S4: Unknown safety state →…, Check if user is legitimately reconsidering. The system must never assume…, Final safety check before response generation. This is the last gate in the…, Map safety block reasons to a NoInterventionReason. Multiple block reasons →…, Executable safety contract encoding invariants S1–S17. This contract is the…, SafetyContract

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
Cohesion: 0.22
Nodes (9): CreateDecisionRequest, DecisionResponse, post, Request, create_decision(), ingest_event(), ConfidenceEvent, DecisionEngine (+1 more)

### Community 69 - "SequenceValidator"
Cohesion: 0.27
Nodes (6): Redis, UUID, Event Ordering. Validates sequence numbers to enforce strict ordering of events…, Validates and tracks event sequence numbers using Redis., Validate that the sequence number is exactly the next expected one. If valid,…, SequenceValidator

### Community 70 - "log.py"
Cohesion: 0.18
Nodes (14): FastAPI, create_app(), lifespan(), FastAPI application entrypoint. Uses the modern lifespan context manager for…, Application lifespan manager — handles startup and shutdown., Create and configure the FastAPI application., get_event_publisher(), Get the event publisher instance. (+6 more)

## Knowledge Gaps
- **90 isolated node(s):** `dwellTimer`, `sessionId`, `telemetry`, `confidence-layer`, `For /graphify add and --watch` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 407 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `InteractionContext` connect `conftest.py` to `create_decision`, `DecisionRequest`, `domain/models.py`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `StateEstimate` connect `StateEstimate` to `domain/models.py`, `conftest.py`, `test_domain.py`, `SafetyContract`, `DecisionContext`, `ActionDefinition`, `enums.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `ActionDefinition` connect `ActionDefinition` to `ActionId`, `domain/models.py`, `ActionRegistry`, `enums.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `StateEstimate` (e.g. with `UncertaintyState` and `.test_audit_contains_full_provenance()`) actually correct?**
  _`StateEstimate` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `DecisionRequest` (e.g. with `create_decision()` and `DecisionEngine`) actually correct?**
  _`DecisionRequest` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `DecisionEngine` (e.g. with `ContextBuilder` and `DecisionRequest`) actually correct?**
  _`DecisionEngine` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 8 INFERRED edges - model-reasoned connections that need verification._