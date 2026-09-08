"""Bounded-cardinality operational measurements; no actor IDs in metric labels."""

from prometheus_client import Counter, Gauge, Histogram

DECISION_REQUESTS = Counter("confidence_decision_requests_total", "Decision requests", ["status"])
DECISION_LATENCY = Histogram(
    "confidence_decision_latency_seconds", "Decision latency", buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.5, 1)
)
EVENT_INGESTION = Counter("confidence_event_ingestion_total", "Events ingested", ["event_type"])
DECISIONS = Counter("confidence_decisions_total", "Decisions by authority results", ["status", "action", "state"])
NO_INTERVENTION = Counter("confidence_no_intervention_total", "Abstention reasons", ["reason"])
SAFETY_BLOCKS = Counter("confidence_safety_blocks_total", "Safety blocks", ["reason"])
HARM_INDICATORS = Counter("confidence_harm_indicators_total", "Observed harm indicators", ["indicator"])
SQS_SCORES = Histogram("confidence_sqs_score", "Session quality scores", buckets=(-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1))
PROVIDER_LATENCY = Histogram("confidence_provider_latency_seconds", "Provider latency", ["provider"])
PROVIDER_ERRORS = Counter("confidence_provider_errors_total", "Provider errors", ["provider"])
CIRCUIT_STATE = Gauge("confidence_circuit_breaker_state", "Closed=0, half-open=1, open=2", ["service"])
AUDIT_ERRORS = Counter("confidence_audit_persistence_errors_total", "Audit persistence errors")
EVENT_ERRORS = Counter("confidence_event_processing_errors_total", "Event processing errors", ["event_type"])
DLQ_MESSAGES = Counter("confidence_dlq_messages_total", "Delivered dead letters", ["reason"])
KILL_SWITCH_STATE = Gauge("confidence_kill_switch_active", "Kill switch active or unavailable")
SHADOW_DECISIONS = Counter("confidence_shadow_decisions_total", "Shadowed decisions")
