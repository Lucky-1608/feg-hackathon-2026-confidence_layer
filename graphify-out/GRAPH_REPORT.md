# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 63 files · ~43,361 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 683 nodes · 1135 edges · 73 communities (38 shown, 32 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 108 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8fa48183`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StateEstimate
- ActionId
- dependencies.py
- DecisionEngine
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
- get_decision_engine
- lifespan
- ActionRegistry
- domain/models.py
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- .get_market_context
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
- UncertaintyState
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
- ActionDefinition
- config.py
- .persist_decision
- BaseModel
- datetime

## God Nodes (most connected - your core abstractions)
1. `DecisionEngine` - 32 edges
2. `DecisionRequest` - 29 edges
3. `StateEstimate` - 28 edges
4. `ActionId` - 26 edges
5. `UncertaintyState` - 19 edges
6. `ConfidenceEvent` - 17 edges
7. `ActionDefinition` - 16 edges
8. `SafetyContract` - 16 edges
9. `HarmIndicators` - 16 edges
10. `ActionRegistry` - 15 edges

## Surprising Connections (you probably didn't know these)
- `engine()` --uses--> `ContextBuilder`  [INFERRED]
  tests/test_engine.py → src/confidence/application/context_builder.py
- `engine()` --uses--> `DummyMarketProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `engine()` --uses--> `DummySlipProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestEndToEndScenarios` --uses--> `DummySlipProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestPropertyInvariants` --uses--> `DummySlipProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py

## Import Cycles
- None detected.

## Communities (73 total, 32 thin omitted)

### Community 0 - "StateEstimate"
Cohesion: 0.08
Nodes (25): Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, TestStateEstimate, datetime, SafetyContext, SafetyContract, Tests for the Safety Contract. Verifies all 17 system invariants (S1–S17) as…, S4: Unknown safety state → fail closed. (+17 more)

### Community 1 - "ActionId"
Cohesion: 0.15
Nodes (12): ActionRegistry, Versioned Action Registry for the Confidence Layer. The Action Registry is the…, Return all registered action IDs., In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Get an action definition by ID., Check if an action is registered (invariant S9)., ActionId, Registered action identifiers. The policy can only select from these registered… (+4 more)

### Community 2 - "dependencies.py"
Cohesion: 0.15
Nodes (22): Protocol, DummyMarketProvider, DummySlipProvider, get_context_builder(), Dependency injection for the API. Wires together domain authorities, provider…, Synthetic slip provider for demo scenarios., Synthetic market provider for demo scenarios., ContextBuilder (+14 more)

### Community 3 - "DecisionEngine"
Cohesion: 0.07
Nodes (39): asyncio, fixture, NoInterventionReason, post, DummySafetyProvider, Synthetic safety provider for demo scenarios. Branches on actor_id — NEVER use…, CreateDecisionRequest, External request payload for a new decision. (+31 more)

### Community 4 - "DecisionContext"
Cohesion: 0.29
Nodes (6): DecisionContext, Complete context assembled by the Context Builder for a decision. This is the…, State Authority. Classifies user uncertainty during betslip confirmation into a…, Deterministic rule-based state estimator. Evaluates the decision context and…, Evaluate context and return the highest priority state estimate., StateEstimator

### Community 5 - "conftest.py"
Cohesion: 0.07
Nodes (48): SafetyContext, UUID, HarmIndicators, MarketContext, OddsSnapshot, BaseModel, Safety-relevant state, sourced from authoritative server-side systems. These…, A user's betslip confirmation session. (+40 more)

### Community 6 - "connection.py"
Cohesion: 0.15
Nodes (16): async_sessionmaker, AsyncSession, Engine, sessionmaker, DatabaseConfig, PostgreSQL connection configuration., create_async_db_engine(), create_async_session_factory() (+8 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "ConfidenceEvent"
Cohesion: 0.16
Nodes (11): BaseModel, datetime, field_validator, EventType, Types of client events the system processes., ConfidenceEvent, Versioned event schema for the Confidence Layer. Events are the primary input…, A versioned event from the client. Schema follows the architecture spec's event… (+3 more)

### Community 9 - "test_domain.py"
Cohesion: 0.07
Nodes (23): SlipContext, Outcome, Output of the Safety Authority. The Safety Authority answers: 'Can we…, Recorded outcome following a decision. Outcomes are submitted via POST…, A single selection within a betslip., SafetyResult, Selection, datetime (+15 more)

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

### Community 20 - "get_decision_engine"
Cohesion: 0.20
Nodes (11): get_action_registry(), get_decision_engine(), get_policy_selector(), get_response_generator(), get_safety_contract(), get_state_estimator(), ActionRegistry, PolicySelector (+3 more)

### Community 21 - "lifespan"
Cohesion: 0.20
Nodes (12): Any, FastAPI, create_app(), lifespan(), FastAPI application entrypoint. Uses the modern lifespan context manager for…, Application lifespan manager — handles startup and shutdown., Create and configure the FastAPI application., configure_logging() (+4 more)

### Community 22 - "ActionRegistry"
Cohesion: 0.11
Nodes (10): ActionRegistry, Tests for the Action Registry. Verifies: - All 6 initial actions are registered…, When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be…, Disabled actions should not appear in eligible lists., NO_INTERVENTION must be eligible for every possible state., When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible., TestActionDefinitions, TestActionEligibility (+2 more)

### Community 23 - "domain/models.py"
Cohesion: 0.19
Nodes (14): OutcomeType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Types of outcomes following a decision., Result of the Safety Authority's evaluation. SAFE: intervention is permitted.…, Return True if this status forces a fail-closed response., Why the Safety Authority blocked an intervention., SafetyBlockReason, SafetyStatus (+6 more)

### Community 24 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 25 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

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

### Community 37 - "DatabasePersistenceProvider"
Cohesion: 0.17
Nodes (10): get_engine(), get_persistence_provider(), AsyncEngine, Get or create the async database engine., DatabasePersistenceProvider, AsyncEngine, Decision, DecisionContext (+2 more)

### Community 49 - "SafetyContract"
Cohesion: 0.16
Nodes (10): NoInterventionReason, Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no…, AuditRecord, Complete audit trail entry for a decision. Stores everything needed to…, Check if state estimation confidence is sufficient. S4: Unknown safety state →…, Check if user is legitimately reconsidering. The system must never assume…, Final safety check before response generation. This is the last gate in the…, Map safety block reasons to a NoInterventionReason. Multiple block reasons →… (+2 more)

### Community 51 - "DecisionContext"
Cohesion: 0.22
Nodes (5): DecisionContext, Harm > everything else., TestPolicySelector, TestResponseGenerator, TestStateEstimator

### Community 52 - "UncertaintyState"
Cohesion: 0.22
Nodes (9): DecisionResponse, InteractionDataPayload, BaseModel, API Data Models. Defines the external API request and response schemas. These…, Interaction payload from the client., External response payload., Return actions eligible for a given state and available data. An action is…, Possible states of user uncertainty during betslip confirmation. The State… (+1 more)

### Community 53 - ".get_safety_context"
Cohesion: 0.22
Nodes (7): SafetyContext, Session, UUID, Fetch safety context (self-exclusion, restrictions, harm indicators)., Provides session metadata., Fetch session metadata., SessionProvider

### Community 68 - "ActionDefinition"
Cohesion: 0.17
Nodes (10): ActionDefinition, BaseModel, Definition of a single registered action. Each action declares: - which…, Return all currently enabled actions., ActionCategory, Semantic categories for actions., PolicySelector, Policy Authority. Selects the best action from a set of safe and eligible… (+2 more)

### Community 69 - "config.py"
Cohesion: 0.20
Nodes (13): AppConfig, DecisionConfig, load_config(), _load_env(), Environment-based configuration for the Confidence Layer. All configuration is…, Load .env file if present., Safety Authority configuration., Decision Engine configuration. (+5 more)

### Community 70 - ".persist_decision"
Cohesion: 0.50
Nodes (3): Decision, DecisionContext, Persist a decision and its audit log to the database.

## Knowledge Gaps
- **90 isolated node(s):** `dwellTimer`, `sessionId`, `telemetry`, `confidence-layer`, `For /graphify add and --watch` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 343 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StateEstimate` connect `StateEstimate` to `ActionDefinition`, `conftest.py`, `DecisionContext`, `test_domain.py`, `SafetyContract`, `DecisionContext`, `UncertaintyState`, `domain/models.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `ActionId` connect `ActionId` to `ActionDefinition`, `.is_conversion_oriented`, `SafetyContract`, `UncertaintyState`, `domain/models.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `DecisionEngine` connect `DecisionEngine` to `dependencies.py`, `.__init__`, `get_decision_engine`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `DecisionEngine` (e.g. with `create_decision()` and `ContextBuilder`) actually correct?**
  _`DecisionEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `DecisionRequest` (e.g. with `create_decision()` and `DecisionEngine`) actually correct?**
  _`DecisionRequest` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `StateEstimate` (e.g. with `UncertaintyState` and `.test_audit_contains_full_provenance()`) actually correct?**
  _`StateEstimate` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 8 INFERRED edges - model-reasoned connections that need verification._