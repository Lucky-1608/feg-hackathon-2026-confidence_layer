"""API routes for the Confidence Layer."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from confidence.api.dependencies import get_decision_engine, get_event_publisher, get_persistence_provider
from confidence.api.models import CreateDecisionRequest, CreateOutcomeRequest, DecisionResponse, OutcomeResponse
from confidence.application.context_builder import DecisionRequest
from confidence.application.engine import DecisionEngine
from confidence.application.reward_join import RewardJoinService
from confidence.config import load_config
from confidence.domain.enums import SafetyStatus
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.domain.models import Outcome
from confidence.domain.sqs import SQSCalculator
from confidence.infrastructure.auth import AuthenticatedUser, bind_session, verify_token
from confidence.infrastructure.event_bus import EventPublisher
from confidence.infrastructure.kill_switch import KillSwitch
from confidence.infrastructure.outbox import OutboxDispatcher
from confidence.infrastructure.persistence import DatabasePersistenceProvider
from confidence.infrastructure.session_state import RedisIdempotencyStore
from confidence.log import get_logger
from confidence.observability.metrics import DECISION_LATENCY, DECISION_REQUESTS, EVENT_INGESTION

logger = get_logger("confidence.api.routes")
router = APIRouter()


def get_idempotency_store(request: Request) -> RedisIdempotencyStore:
    return RedisIdempotencyStore(request.app.state.redis)


@router.post(
    "/v1/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new decision",
    description="Evaluate betslip context and determine the appropriate intervention.",
)
async def create_decision(
    request: CreateDecisionRequest,
    http_request: Request,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    engine: DecisionEngine = Depends(get_decision_engine),  # noqa: B008
    idemp_store: RedisIdempotencyStore = Depends(get_idempotency_store),  # noqa: B008
    user_id: AuthenticatedUser = Depends(verify_token),  # noqa: B008
) -> DecisionResponse | JSONResponse:
    """Handle a decision request."""
    actor_id = await bind_session(http_request, user_id, request.anonymous_actor_id, request.session_id, "decisions:write")
    if idempotency_key:
        import hashlib

        idempotency_key = user_id.actor_id + ":" + hashlib.sha256(idempotency_key.encode()).hexdigest()
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
            anonymous_actor_id=actor_id,
            client_version=request.client_version,
            slip_id=request.slip_id,
            interaction=InteractionContext(**request.interaction.model_dump(exclude_unset=True)),
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
    user_id: AuthenticatedUser = Depends(verify_token),  # noqa: B008
) -> dict[str, str]:
    actor_id = await bind_session(req, user_id, event.anonymous_actor_id, event.session_id, "events:write")
    event = event.model_copy(update={"anonymous_actor_id": actor_id})
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


@router.post("/v1/outcomes", response_model=OutcomeResponse, status_code=201)
async def create_outcome(
    request: CreateOutcomeRequest,
    persistence: DatabasePersistenceProvider = Depends(get_persistence_provider),  # noqa: B008
    publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008
    user_id: AuthenticatedUser = Depends(verify_token),  # noqa: B008
) -> OutcomeResponse:
    user_id.require_scope("outcomes:write")
    decision = await persistence.get_decision(request.decision_id)
    if decision is None or decision.session_id != request.session_id:
        raise HTTPException(status_code=404, detail="Decision not found")
    owned_context = await persistence.get_context(request.decision_id)
    if owned_context is None or (not user_id.is_demo and owned_context.session.anonymous_actor_id != user_id.actor_id):
        raise HTTPException(status_code=404, detail="Decision not found")
    now = datetime.now(UTC)
    latency = max(0, int((now - decision.timestamp).total_seconds() * 1000))
    late = latency > 300000
    outcome = Outcome(
        outcome_id=request.outcome_id or uuid4(),
        timestamp=now,
        **request.model_dump(exclude={"outcome_id", "metadata"}),
        metadata={**request.metadata, "join_latency_ms": latency, "is_late_join": late},
    )
    calculator = SQSCalculator(load_config().sqs)
    try:
        score = calculator.compute_sqs(decision, outcome, owned_context.safety, await persistence.get_events(outcome.session_id))
        messages = [("confidence.outcomes", outcome.model_dump(mode="json"))]
        if not late and not decision.shadow_mode and decision.safety_status == SafetyStatus.SAFE:
            reward = RewardJoinService.build_signal(decision, outcome, owned_context, latency)
            messages.append(("confidence.rewards", reward.model_dump(mode="json")))
        await persistence.record_outcome_bundle(outcome, score, calculator.config.version, messages)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="Outcome ID already used") from exc
    except Exception as exc:
        logger.error("outcome_ingestion_failed", outcome_id=str(outcome.outcome_id))
        raise HTTPException(status_code=503, detail="Outcome ingestion unavailable") from exc
    # Eager delivery is bounded. A durable outbox worker retries broker failures.
    try:
        import asyncio

        async with asyncio.timeout(0.1):
            await OutboxDispatcher(persistence, publisher).flush()
    except Exception:
        logger.warning("outcome_delivery_deferred")

    return OutcomeResponse(outcome_id=outcome.outcome_id, decision_id=outcome.decision_id)


@router.get("/v1/metrics/sqs")
async def sqs_metrics(
    window: str = Query(default="24h", pattern=r"^[1-9][0-9]{0,2}h$"),
    persistence: DatabasePersistenceProvider = Depends(get_persistence_provider),  # noqa: B008
    user_id: AuthenticatedUser = Depends(verify_token),  # noqa: B008
) -> dict[str, Any]:
    user_id.require_scope("metrics:read")
    return await persistence.sqs_metrics(int(window[:-1]), actor_id=None if user_id.is_demo else user_id.actor_id)


@router.post("/v1/admin/kill-switch")
async def toggle_kill_switch(
    request: Request,
    action: Literal["activate", "deactivate"],
    reason: str = "",
    user: AuthenticatedUser = Depends(verify_token),  # noqa: B008
) -> dict[str, bool]:
    user.require_scope("admin:global")
    switch = KillSwitch(request.app.state.redis)
    if action == "activate":
        await switch.activate(reason, user.actor_id)
    else:
        await switch.deactivate()
    return {"active": await switch.is_active()}
