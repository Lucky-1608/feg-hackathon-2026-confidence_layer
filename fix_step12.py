import os

os.makedirs("src/confidence/observability", exist_ok=True)

with open("src/confidence/observability/__init__.py", "w") as f:
    f.write('"""Observability module."""\n')

with open("src/confidence/observability/tracing.py", "w") as f:
    f.write('''"""OpenTelemetry tracing setup."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

def setup_tracing(service_name: str = "confidence_layer") -> None:
    """Initialize OpenTelemetry tracing."""
    provider = TracerProvider()
    # In production, use OTLPSpanExporter
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

def get_tracer(name: str) -> trace.Tracer:
    return trace.get_tracer(name)
''')

with open("src/confidence/observability/metrics.py", "w") as f:
    f.write('''"""Prometheus metrics."""

from prometheus_client import Counter, Histogram

DECISION_REQUESTS = Counter(
    "confidence_decision_requests_total",
    "Total number of decision requests",
    ["status"]
)

DECISION_LATENCY = Histogram(
    "confidence_decision_latency_seconds",
    "Latency of decision requests in seconds"
)

EVENT_INGESTION = Counter(
    "confidence_event_ingestion_total",
    "Total events ingested",
    ["event_type"]
)
''')

# Update api/routes.py to use metrics
with open("src/confidence/api/routes.py", "r") as f:
    routes = f.read()

if "from confidence.observability.metrics import DECISION_REQUESTS, DECISION_LATENCY, EVENT_INGESTION" not in routes:
    routes = "from confidence.observability.metrics import DECISION_REQUESTS, DECISION_LATENCY, EVENT_INGESTION\nimport time\n" + routes
    
    # Update create_decision
    routes = routes.replace(
        "async def create_decision(\n    request: CreateDecisionRequest,",
        "async def create_decision(\n    request: CreateDecisionRequest,"
    )
    routes = routes.replace(
        "    if idempotency_key:",
        "    start_time = time.time()\n    if idempotency_key:"
    )
    routes = routes.replace(
        "        return response",
        "        DECISION_REQUESTS.labels(status=\"success\").inc()\n        DECISION_LATENCY.observe(time.time() - start_time)\n        return response"
    )
    routes = routes.replace(
        "    except ValidationError as e:",
        "    except ValidationError as e:\n        DECISION_REQUESTS.labels(status=\"error_validation\").inc()\n        DECISION_LATENCY.observe(time.time() - start_time)"
    )
    routes = routes.replace(
        "    except Exception as e:",
        "    except Exception as e:\n        DECISION_REQUESTS.labels(status=\"error_internal\").inc()\n        DECISION_LATENCY.observe(time.time() - start_time)"
    )

    # Update ingest_event
    routes = routes.replace(
        "        await publisher.publish(event)",
        "        await publisher.publish(event)\n        EVENT_INGESTION.labels(event_type=event.event_type.value).inc()"
    )

    with open("src/confidence/api/routes.py", "w") as f:
        f.write(routes)

