import os

os.makedirs(".github/workflows", exist_ok=True)
with open(".github/workflows/ci.yml", "w") as f:
    f.write('''name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Run tests
        run: make check
''')

os.makedirs("k8s", exist_ok=True)
with open("k8s/deployment.yaml", "w") as f:
    f.write('''apiVersion: apps/v1
kind: Deployment
metadata:
  name: confidence-layer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: confidence-layer
  template:
    metadata:
      labels:
        app: confidence-layer
    spec:
      containers:
        - name: confidence-layer
          image: confidence-layer:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: confidence-secrets
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
''')

os.makedirs("tests/load", exist_ok=True)
with open("tests/load/locustfile.py", "w") as f:
    f.write('''from locust import HttpUser, task, between

class ConfidenceUser(HttpUser):
    wait_time = between(0.1, 1.0)
    
    @task
    def decide(self):
        self.client.post("/v1/decisions", 
            json={
                "session_id": "00000000-0000-0000-0000-000000000000",
                "anonymous_actor_id": "actor-001",
                "client_version": "1.0",
                "slip_id": "slip-001",
                "interaction": {
                    "session_age_seconds": 120.0,
                    "recent_backtracks": 1,
                    "dwell_time_seconds": 15.0,
                    "selection_changes": 0,
                    "stake_changes": 0,
                    "odds_changed": True,
                    "time_since_slip_creation_seconds": 60.0,
                    "confirmation_attempts": 2,
                    "interaction_velocity": 3.0
                }
            },
            headers={"Authorization": "Bearer demo-token"}
        )
''')

# Update README.md
with open("README.md", "a") as f:
    f.write('''

## Production Architecture (Phase 4)
- **Infrastructure**: Kafka (Redpanda) for events/audit, Redis for idempotency/state, PostgreSQL for persistence.
- **Resilience**: Circuit breakers, timeouts, rate limiting.
- **Security**: OAuth2 Bearer token authentication, Zero-PII by design.
- **Observability**: OpenTelemetry tracing, Prometheus metrics.
- **Deployment**: Kubernetes ready with liveness/readiness probes.
''')

# Create architecture doc
os.makedirs("docs", exist_ok=True)
with open("docs/ARCHITECTURE.md", "w") as f:
    f.write('''# Architecture

The Confidence Layer implements a Hexagonal Architecture (Ports and Adapters).
- **Core Domain**: Pure Python, zero dependencies (enums, rules, policy).
- **Application**: Orchestration layer (Decision Engine, Context Builder).
- **Infrastructure**: External adapters (Redis, Kafka, Postgres).

## Critical Path
The critical path (`POST /v1/decisions`) is completely isolated from background tasks (Audit Logging, Event Ingestion). If Kafka is down, decisions still process (fail-open for audit). If Safety Provider is down, decisions fail-closed.
''')

