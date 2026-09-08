# Architecture

The Confidence Layer implements a Hexagonal Architecture (Ports and Adapters).
- **Core Domain**: Pure Python, zero dependencies (enums, rules, policy).
- **Application**: Orchestration layer (Decision Engine, Context Builder).
- **Infrastructure**: External adapters (Redis, Kafka, Postgres).

## Critical Path
The critical path (`POST /v1/decisions`) is completely isolated from background tasks (Audit Logging, Event Ingestion). If Kafka is down, decisions still process (fail-open for audit). If Safety Provider is down, decisions fail-closed.
