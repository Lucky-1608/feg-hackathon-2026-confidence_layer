"""Domain model re-exports for convenience."""

from confidence.domain.actions import ActionDefinition, ActionRegistry
from confidence.domain.enums import (
    ActionCategory,
    ActionId,
    EventType,
    NoInterventionReason,
    OutcomeType,
    SafetyBlockReason,
    SafetyStatus,
    UncertaintyState,
)
from confidence.domain.events import ConfidenceEvent
from confidence.domain.models import (
    AuditRecord,
    Decision,
    DecisionContext,
    HarmIndicators,
    InteractionContext,
    MarketContext,
    OddsSnapshot,
    Outcome,
    SafetyContext,
    SafetyResult,
    Selection,
    Session,
    SlipContext,
    StateEstimate,
)
from confidence.domain.safety import SafetyContract

__all__ = [
    # Enums
    "ActionCategory",
    "ActionId",
    "EventType",
    "NoInterventionReason",
    "OutcomeType",
    "SafetyBlockReason",
    "SafetyStatus",
    "UncertaintyState",
    # Models
    "AuditRecord",
    "Decision",
    "DecisionContext",
    "HarmIndicators",
    "InteractionContext",
    "MarketContext",
    "OddsSnapshot",
    "Outcome",
    "SafetyContext",
    "SafetyResult",
    "Selection",
    "Session",
    "SlipContext",
    "StateEstimate",
    # Events
    "ConfidenceEvent",
    # Actions
    "ActionDefinition",
    "ActionRegistry",
    # Safety
    "SafetyContract",
]
