# Confidence Layer

## 1. Team Name, Challenge Entered and Short Solution Title
**Team Name:** The Decisioning Team (Sai Sharath, Saketh, Hrishikesh)
**Challenge:** FEG Innovation Hackathon 2026 Challenge 1 — Session Quality and Session-to-Action Conversion
**Solution Title:** Confidence Layer — A safety-constrained, real-time decision engine to resolve betslip hesitation.

## 2. Problem Statement
Users reach the betslip confirm button and abandon their sessions at the final step. Traditional conversion optimization pushes urgency or social proof, creating a motivation gap and leading to dark patterns. However, hesitation at confirmation is actually an *information gap* (e.g., "Did the odds change?", "What does this market mean?"). The challenge is turning sessions into confident actions without pressuring players, while rigorously respecting Responsible Gambling (RG) limits.

## 3. Solution Overview and Key Innovation
Confidence Layer is a sub-100ms real-time decision engine that classifies player uncertainty and surfaces factual clarifications (or deliberately stays silent). 
**Key Innovation:** Compliance as a mathematical property. The engine uses a Session Quality Score (SQS) where the penalty for harm indicators mathematically outweighs any conversion value. Safety checks act as hard gates *before* policy evaluation, meaning the system is structurally incapable of recommending unsafe interventions.

## 4. Key Features / User Journey
1. **Hesitation Detection:** The user hesitates on the betslip.
2. **Context Assembly:** The system gathers session history, market data, and RG limits.
3. **Safety Gate:** Evaluates strict safety invariants (e.g., self-exclusion, escalating stakes). If blocked, defaults to `NO_INTERVENTION`.
4. **State Classification:** A LightGBM model classifies the uncertainty (e.g., `ODDS_CHANGE`, `MARKET_MEANING`, `LEGITIMATE_RECONSIDERATION`).
5. **Policy Selection:** A Contextual Bandit (Vowpal Wabbit) selects the optimal safe intervention.
6. **Factual Response:** A template-based response is presented to the user (No LLM hallucinations).

## 5. Technology Stack
*   **Backend:** Python 3.12+, FastAPI, Pydantic v2
*   **Architecture:** Hexagonal (Ports & Adapters)
*   **ML Pipeline:** LightGBM (classification), Vowpal Wabbit (contextual bandit)
*   **Data & State:** PostgreSQL (audit), Redis (ephemeral session state, rate limits), Redpanda/Kafka (event bus)
*   **Observability:** Prometheus, OpenTelemetry, Structlog

## 6. System Requirements and Prerequisites
*   Docker and Docker Compose
*   Python 3.12+ (if running locally without Docker)
*   Make

## 7. Installation / Setup Steps
1. Clone the repository.
2. Copy the environment variables: `cp .env.example .env`
3. Boot the infrastructure and application using Docker: `make docker-up`

## 8. Environment Variables and Configuration Instructions
All non-secret configurations are detailed in `.env.example`. Key toggles:
*   `POLICY_TYPE`: Set to `deterministic` or `bandit`.
*   `STATE_ESTIMATOR_TYPE`: Set to `rules` or `lgbm`.
*   `SHADOW_MODE`: Set to `off` to present actions to the UI, or `full` to audit decisions silently.

## 9. How to Run the Prototype
If using Docker, the application runs automatically on port 8000.
To run the API natively (after starting infrastructure via `make infra-up`): `make run`
To run the background event and bandit workers: `make run-worker`

## 10. How to Test / Validate the Prototype
We maintain a strict >75% branch coverage floor. Run the full validation suite: `make check`. This executes Ruff linting, Mypy type checking, and Pytest coverage testing.

## 11. Demo Instructions or Demo Flow
1. Navigate to `http://localhost:8000/ui/` in your browser.
2. On the **Scenario Controls** panel, toggle different states (e.g., `Odds Changed`, `Safety State -> Self Excluded`).
3. Click the betslip and observe the **Pipeline Visualization**.
4. You will see the system gracefully navigate the hard gates, classifying the state and rendering `NO_INTERVENTION` when safety flags are triggered.

## 12. Known Limitations, Assumptions and Future Improvements
*   **Operator Adapters:** The current providers (`SafetyProvider`, `SlipProvider`, `MarketProvider`) are dummy adapters. In production, these must connect to FEG's real internal APIs.
*   **Auth Integration:** JWT validation is implemented, but requires integration with FEG's identity provider for production JWKS endpoints.

## 13. Required Documentation Links
*   [Architecture & Technical Overview](docs/architecture.md)
*   [Impact Case & Cost-Value Analysis](docs/impact-case.md)
*   [Compliance Analysis](docs/compliance-note.md)
*   [Dependencies & AI Disclosure](docs/dependencies.md)
