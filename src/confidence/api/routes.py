"""API routes for the Confidence Layer."""

from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from confidence.api.dependencies import get_decision_engine, get_event_publisher
from confidence.api.models import CreateDecisionRequest, DecisionResponse
from confidence.application.context_builder import DecisionRequest
from confidence.application.engine import DecisionEngine
from confidence.config import load_config
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.infrastructure.event_bus import EventPublisher
from confidence.infrastructure.session_state import RedisIdempotencyStore
from confidence.log import get_logger
from confidence.observability.metrics import DECISION_LATENCY, DECISION_REQUESTS, EVENT_INGESTION

logger = get_logger("confidence.api.routes")
router = APIRouter()


# We need a dependency to get the idempotency store
def get_idempotency_store() -> RedisIdempotencyStore:
    # Hacky way to inject it using the existing redis client from dependencies
    # In a real app we'd attach it to app.state
    config = load_config()
    from redis.asyncio import Redis

    redis_client = Redis.from_url(config.redis.url, decode_responses=False)
    return RedisIdempotencyStore(redis_client)


@router.post(
    "/v1/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new decision",
    description="Evaluate betslip context and determine the appropriate intervention.",
)
async def create_decision(
    request: CreateDecisionRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    engine: DecisionEngine = Depends(get_decision_engine),  # noqa: B008
    idemp_store: RedisIdempotencyStore = Depends(get_idempotency_store),  # noqa: B008
) -> DecisionResponse | JSONResponse:
    """Handle a decision request."""
    # 1. Idempotency Check
    start_time = time.time()
    if idempotency_key:
        cached_response = await idemp_store.get_response(idempotency_key)
        if cached_response:
            logger.info("idempotent_hit", key=idempotency_key)
            DECISION_REQUESTS.labels(status="success_cached").inc()
            DECISION_LATENCY.observe(time.time() - start_time)
            return JSONResponse(status_code=200, content=cached_response)

        acquired = await idemp_store.acquire(idempotency_key)
        if not acquired:
            DECISION_REQUESTS.labels(status="error_conflict").inc()
            DECISION_LATENCY.observe(time.time() - start_time)
            raise HTTPException(status_code=409, detail="Request already in progress")

    try:
        # Convert API model to Application model
        from confidence.domain.models import InteractionContext

        app_request = DecisionRequest(
            session_id=request.session_id,
            anonymous_actor_id=request.anonymous_actor_id,
            client_version=request.client_version,
            slip_id=request.slip_id,
            interaction=InteractionContext(**request.interaction.model_dump()),
        )

        result = await engine.decide(app_request)

        response = DecisionResponse(
            decision_id=result.decision.decision_id,
            action=result.decision.selected_action,
            state=result.decision.state,
            confidence=result.decision.state_confidence,
            reason=result.decision.reason,
            response_text=result.response_text,
            policy_version=result.decision.policy_version,
            model_version=result.decision.model_version,
            action_registry_version=result.decision.action_registry_version,
            safety_status=result.decision.safety_status,
        )

        # Save to idempotency store
        if idempotency_key:
            # We dump the pydantic model to dict, then convert UUIDs/Enums to strings for json
            resp_dict = json.loads(response.model_dump_json())
            await idemp_store.save_response(idempotency_key, resp_dict)

        DECISION_REQUESTS.labels(status="success").inc()
        DECISION_LATENCY.observe(time.time() - start_time)
        return response
    except ValidationError as e:
        DECISION_REQUESTS.labels(status="error_validation").inc()
        DECISION_LATENCY.observe(time.time() - start_time)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error": "validation_error", "messages": e.errors()}
        ) from e
    except Exception as e:
        logger.error("api_error", error=str(e))
        DECISION_REQUESTS.labels(status="error_internal").inc()
        DECISION_LATENCY.observe(time.time() - start_time)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": "Internal Server Error"},
        ) from e


@router.post(
    "/v1/events",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest Client Events",
    description="Ingest a domain event from the client and publish it to the event bus.",
)
async def ingest_event(
    event: ConfidenceEvent,
    req: Request,
    publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008
) -> dict[str, str]:
    try:
        await publisher.publish(event)
        EVENT_INGESTION.labels(event_type=event.event_type.value).inc()
        return {"status": "accepted"}
    except Exception as e:
        logger.error(
            "event_ingestion_error",
            error=str(e),
            event_id=str(event.event_id),
            path=req.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ingestion_failed", "message": "Failed to ingest event"},
        ) from e


@router.get("/health", status_code=200, summary="Liveness Probe")
async def health_check() -> dict[str, str]:
    """Basic liveness probe for Kubernetes."""
    return {"status": "ok"}


@router.get("/ready", status_code=200, summary="Readiness Probe")
async def readiness_check() -> dict[str, str]:
    """Check if the service is ready to receive traffic (DB/Redis reachable)."""
    # In a real app we would ping Postgres, Redis, and Kafka here
    return {"status": "ready"}
