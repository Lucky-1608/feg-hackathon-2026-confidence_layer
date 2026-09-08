"""Prometheus metrics."""

from prometheus_client import Counter, Histogram

DECISION_REQUESTS = Counter("confidence_decision_requests_total", "Total number of decision requests", ["status"])

DECISION_LATENCY = Histogram("confidence_decision_latency_seconds", "Latency of decision requests in seconds")

EVENT_INGESTION = Counter("confidence_event_ingestion_total", "Total events ingested", ["event_type"])
