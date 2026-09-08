# Dependencies and Open Source Disclosure

## Third-Party Libraries and SDKs
The following open-source components are utilized under their respective licenses:
*   **FastAPI / Pydantic / Uvicorn:** Core HTTP application framework (MIT License).
*   **SQLAlchemy / Alembic:** PostgreSQL ORM and database migrations (MIT License).
*   **LightGBM:** Used for the `HesitationClassifier` state estimation (MIT License).
*   **Vowpal Wabbit:** Used for the `ContextualBandit` policy selection (BSD 3-Clause License).
*   **Redis-py / aiokafka:** Adapters for state and event buses (MIT / Apache 2.0).

## Datasets and Models
*   **Harm Indicator Data:** Features are mapped against the structure of the Transparency Project bwin datasets for research-backed problem gambling indicators.
*   **Hackathon Datasets:** `EPS_Offers.csv` and `top_casino_users_event_logs.csv` (provided by FEG) are used to train the LightGBM models locally. These datasets are NOT committed to this repository.

## AI and Code Assistant Disclosure
*   Generative AI tools (Claude, Gemini, GPT Astra) were used as coding assistants to construct boilerplate code, implement standard interfaces (Ports & Adapters), and generate documentation following the Hackathon's allowed use policies.
*   The team remains responsible for the originality, security, and accuracy of the final compiled architecture. No LLM models execute on the runtime critical path.
