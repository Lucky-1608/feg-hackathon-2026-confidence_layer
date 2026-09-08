# Graph Report - Confidence  (2026-09-04)

## Corpus Check
- 63 files · ~43,354 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 655 nodes · 1258 edges · 51 communities (33 shown, 15 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 160 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6874b8f3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SafetyContract
- ActionRegistry
- context_builder.py
- DecisionEngine
- DecisionContext
- SafetyContext
- connection.py
- TestSchemaCreation
- enums.py
- UncertaintyState
- Interactive UI & Client Telemetry
- Conversion Safety Rules
- Package Init (Confidence)
- Confidence Layer Root
- What You Must Do When Invoked
- What You Must Do When Invoked
- ._build_failure_decision
- dependencies.py
- PersistenceProvider
- config.py
- lifespan
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- DummyMarketProvider
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
- UUID
- Protocol

## God Nodes (most connected - your core abstractions)
1. `SafetyContract` - 50 edges
2. `ActionRegistry` - 49 edges
3. `ActionId` - 41 edges
4. `UncertaintyState` - 33 edges
5. `DecisionEngine` - 29 edges
6. `SafetyContext` - 29 edges
7. `StateEstimate` - 29 edges
8. `NoInterventionReason` - 24 edges
9. `DecisionContext` - 24 edges
10. `SafetyStatus` - 23 edges

## Surprising Connections (you probably didn't know these)
- `engine()` --uses--> `DummyMarketProvider`  [INFERRED]
  tests/test_engine.py → src/confidence/api/dependencies.py
- `TestDecision` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_domain.py → src/confidence/domain/enums.py
- `TestAdversarialAndFailures` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/enums.py
- `TestEndToEndScenarios` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/enums.py
- `TestPropertyInvariants` --uses--> `NoInterventionReason`  [INFERRED]
  tests/test_engine.py → src/confidence/domain/enums.py

## Import Cycles
- None detected.

## Communities (51 total, 15 thin omitted)

### Community 0 - "SafetyContract"
Cohesion: 0.07
Nodes (31): NoInterventionReason, Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no…, Output of the State Authority. The State Authority answers: 'What is…, StateEstimate, Check if state estimation confidence is sufficient. S4: Unknown safety state →…, Check if user is legitimately reconsidering. The system must never assume…, Final safety check before response generation. This is the last gate in the…, Map safety block reasons to a NoInterventionReason. Multiple block reasons →… (+23 more)

### Community 1 - "ActionRegistry"
Cohesion: 0.06
Nodes (28): ActionDefinition, ActionRegistry, BaseModel, Return all registered action IDs., Definition of a single registered action. Each action declares: - which…, In-memory registry of all valid actions. Invariants enforced: - S9: Policy can…, Get an action definition by ID., Check if an action is registered (invariant S9). (+20 more)

### Community 2 - "context_builder.py"
Cohesion: 0.11
Nodes (19): ContextBuilder, Context Builder. Constructs the DecisionContext from the incoming request and…, Builds a complete, trustworthy DecisionContext., Construct the context safely., State of the betslip at decision time., SlipContext, MarketProvider, Protocol (+11 more)

### Community 3 - "DecisionEngine"
Cohesion: 0.08
Nodes (38): asyncio, post, SafetyProvider, SlipProvider, DummySafetyProvider, DummySlipProvider, Synthetic safety provider for demo scenarios. Branches on actor_id — NEVER use…, Synthetic slip provider for demo scenarios. (+30 more)

### Community 4 - "DecisionContext"
Cohesion: 0.19
Nodes (9): DecisionContext, Complete context assembled by the Context Builder for a decision. This is the…, State Authority. Classifies user uncertainty during betslip confirmation into a…, Deterministic rule-based state estimator. Evaluates the decision context and…, Evaluate context and return the highest priority state estimate., StateEstimator, TestDecisionContext, Harm > everything else. (+1 more)

### Community 5 - "SafetyContext"
Cohesion: 0.07
Nodes (41): SafetyContext, HarmIndicators, MarketContext, Safety-relevant state, sourced from authoritative server-side systems. These…, Authoritative market data for a selection., Behavioral indicators of potential gambling harm. These are derived from…, Return True if any harm indicator is present., SafetyContext (+33 more)

### Community 6 - "connection.py"
Cohesion: 0.15
Nodes (16): async_sessionmaker, AsyncSession, Engine, sessionmaker, DatabaseConfig, PostgreSQL connection configuration., create_async_db_engine(), create_async_session_factory() (+8 more)

### Community 7 - "TestSchemaCreation"
Cohesion: 0.11
Nodes (6): Database schema for the Confidence Layer. Uses SQLAlchemy Core table…, Tests for the database schema. Verifies that the SQLAlchemy schema creates all…, create_all should be safe to call multiple times., Verify all tables can be created and have correct structure., All 9 required tables must be created., TestSchemaCreation

### Community 8 - "enums.py"
Cohesion: 0.10
Nodes (18): field_validator, Versioned Action Registry for the Confidence Layer. The Action Registry is the…, ActionCategory, EventType, Domain enumerations for the Confidence Layer. All domain-level enum types are…, Semantic categories for actions., Types of client events the system processes., ConfidenceEvent (+10 more)

### Community 9 - "UncertaintyState"
Cohesion: 0.08
Nodes (38): SlipContext, OutcomeType, Types of outcomes following a decision., Possible states of user uncertainty during betslip confirmation. The State…, Result of the Safety Authority's evaluation. SAFE: intervention is permitted.…, Why the Safety Authority blocked an intervention., SafetyBlockReason, SafetyStatus (+30 more)

### Community 10 - "Interactive UI & Client Telemetry"
Cohesion: 0.22
Nodes (5): dwellTimer, evaluateDecision(), sessionId, telemetry, updatePipeline()

### Community 11 - "Conversion Safety Rules"
Cohesion: 0.36
Nodes (3): Return True if an action is conversion-oriented. NO_INTERVENTION and…, Test which actions are classified as conversion-oriented., TestConversionOrientation

### Community 17 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 18 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 19 - "._build_failure_decision"
Cohesion: 0.17
Nodes (11): DecisionRequest, NoInterventionReason, DecisionResult, Decision, DecisionContext, Schedule audit persistence as a background task. This is intentionally fire-…, The core orchestration logic., Compute which data keys are actually available from authoritative sources. Only… (+3 more)

### Community 20 - "dependencies.py"
Cohesion: 0.18
Nodes (16): get_action_registry(), get_decision_engine(), get_engine(), get_persistence_provider(), get_policy_selector(), get_response_generator(), get_safety_contract(), get_state_estimator() (+8 more)

### Community 21 - "PersistenceProvider"
Cohesion: 0.19
Nodes (10): Protocol, PersistenceProvider, Decision Engine Orchestrator. Coordinates the complete end-to-end pipeline: 1.…, Interface for async audit logging., DatabasePersistenceProvider, AsyncEngine, Persistence for audit logs and decisions. Architectural constraint: Persistence…, Saves decisions and audit records asynchronously to the database. All column… (+2 more)

### Community 22 - "config.py"
Cohesion: 0.20
Nodes (13): AppConfig, DecisionConfig, load_config(), _load_env(), Environment-based configuration for the Confidence Layer. All configuration is…, Load .env file if present., Safety Authority configuration., Decision Engine configuration. (+5 more)

### Community 23 - "lifespan"
Cohesion: 0.21
Nodes (11): Any, FastAPI, create_app(), lifespan(), FastAPI application entrypoint. Uses the modern lifespan context manager for…, Application lifespan manager — handles startup and shutdown., Create and configure the FastAPI application., configure_logging() (+3 more)

### Community 24 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 25 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 26 - "DummyMarketProvider"
Cohesion: 0.29
Nodes (6): MarketContext, MarketProvider, DummyMarketProvider, get_context_builder(), ContextBuilder, Synthetic market provider for demo scenarios.

### Community 27 - ".__init__"
Cohesion: 0.29
Nodes (6): ActionRegistry, ContextBuilder, PolicySelector, ResponseGenerator, SafetyContract, StateEstimator

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

## Knowledge Gaps
- **90 isolated node(s):** `graphify`, `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 320 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DecisionEngine` connect `DecisionEngine` to `.__init__`, `._build_failure_decision`, `dependencies.py`, `PersistenceProvider`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `ActionRegistry` connect `ActionRegistry` to `enums.py`, `UncertaintyState`, `DecisionEngine`, `SafetyContext`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `SafetyContract` connect `SafetyContract` to `ActionRegistry`, `DecisionEngine`, `SafetyContext`, `UncertaintyState`, `Conversion Safety Rules`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `SafetyContract` (e.g. with `ActionId` and `NoInterventionReason`) actually correct?**
  _`SafetyContract` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ActionRegistry` (e.g. with `ActionId` and `UncertaintyState`) actually correct?**
  _`ActionRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `ActionId` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`ActionId` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `UncertaintyState` (e.g. with `DecisionResponse` and `ActionDefinition`) actually correct?**
  _`UncertaintyState` has 22 INFERRED edges - model-reasoned connections that need verification._