# Architecture & Technical Overview

## Hexagonal Architecture
Confidence Layer implements a Ports and Adapters (Hexagonal) architecture to strictly separate pure business logic from infrastructure.
*   **Domain Layer:** Contains all state estimation, policy rules, and safety invariants. It has no external dependencies.
*   **Application Layer:** Orchestrates the 10-step pipeline (`DecisionEngine`) with strict sub-100ms timeouts.
*   **Infrastructure Layer:** Implements adapters for Redis, PostgreSQL, and Kafka.

## The Three Authorities
The decision pipeline is strictly ordered:
1.  **Safety Authority (Can we?):** Evaluates 17 safety invariants. Hard blocks prevent any intervention.
2.  **State Authority (What's happening?):** Uses a LightGBM classifier (or deterministic fallback rules) to map telemetry to an `UncertaintyState`.
3.  **Policy Authority (Which action?):** Uses a Vowpal Wabbit contextual bandit to select an action from the pre-filtered, safe candidate set.

## Data Flow & Deployment
*   **PostgreSQL:** Stores persistent session data, decision audits, and outcomes. 
*   **Redis:** Manages sub-millisecond ephemeral session state, idempotency locks, and rate limits.
*   **Kafka / Redpanda:** Durable event bus for background workers (Bandit Trainer, Event Consumer).
*   **Docker:** The entire application is containerized and orchestratable via Kubernetes or Docker Compose.
