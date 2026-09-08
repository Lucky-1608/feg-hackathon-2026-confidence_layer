"""API routes for the Confidence Layer."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError

from confidence.api.dependencies import get_decision_engine
from confidence.api.models import CreateDecisionRequest, DecisionResponse
from confidence.application.context_builder import DecisionRequest
from confidence.application.engine import DecisionEngine
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.log import get_logger

router = APIRouter()


@router.post(
    "/v1/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new decision",
    description="Evaluate betslip context and determine the appropriate intervention.",
)
async def create_decision(
    request: CreateDecisionRequest,
    engine: DecisionEngine = Depends(get_decision_engine),  # noqa: B008
) -> DecisionResponse:
    """Handle a decision request."""
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

        return DecisionResponse(
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
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except Exception as e:
        # In production this should be logged and return a generic 500
        # However, the engine catches all exceptions and fails closed anyway,
        # so this is just a final safety net for the router itself.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from e


logger = get_logger("confidence.api.routes")


@router.post(
    "/v1/events",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest Client Events",
    description="Ingest a domain event from the client and publish it to the event bus.",
)
async def ingest_event(
    event: ConfidenceEvent,
    request: Request,
) -> dict[str, str]:
    try:
        from confidence.api.dependencies import get_event_publisher

        publisher = get_event_publisher()
        await publisher.publish(event)
        return {"status": "accepted"}
    except Exception as e:
        logger.error(
            "event_ingestion_error",
            error=str(e),
            event_id=str(event.event_id),
            path=request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest event",
        ) from e
