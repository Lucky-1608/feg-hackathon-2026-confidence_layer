"""Optional OTLP tracing with process-scoped provider initialization."""

from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from sqlalchemy.ext.asyncio import AsyncEngine

_provider: TracerProvider | None = None


def setup_tracing(service_name: str = "confidence_layer", otlp_endpoint: str | None = None) -> TracerProvider:
    global _provider
    if _provider is None:
        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        if otlp_endpoint:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            exporter: Any = OTLPSpanExporter(endpoint=otlp_endpoint)
        else:
            exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _provider = provider
    return _provider


def instrument_app(app: FastAPI, engine: AsyncEngine, redis: Any = None) -> None:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    RedisInstrumentor().instrument()


def get_tracer(name: str) -> trace.Tracer:
    return trace.get_tracer(name)
