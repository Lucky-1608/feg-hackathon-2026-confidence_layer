"""Domain enumerations for the Confidence Layer.

All domain-level enum types are defined here to avoid circular imports
and to serve as the single source of truth for valid enum values.
"""

from enum import StrEnum


class UncertaintyState(StrEnum):
    """Possible states of user uncertainty during betslip confirmation.

    The State Authority classifies the user's hesitation into one of these
    categories. The classification drives action eligibility.
    """

    UNKNOWN = "UNKNOWN"
    MARKET_MEANING = "MARKET_MEANING"
    ODDS_CHANGE = "ODDS_CHANGE"
    SLIP_CONFIGURATION = "SLIP_CONFIGURATION"
    STAKE_RETURN = "STAKE_RETURN"
    GENERAL_UI_FRICTION = "GENERAL_UI_FRICTION"
    LEGITIMATE_RECONSIDERATION = "LEGITIMATE_RECONSIDERATION"
    DISTRACTION = "DISTRACTION"
    POTENTIAL_HARM = "POTENTIAL_HARM"
    NO_UNCERTAINTY = "NO_UNCERTAINTY"


class SafetyStatus(StrEnum):
    """Result of the Safety Authority's evaluation.

    SAFE: intervention is permitted.
    BLOCKED: intervention is prohibited for a specific reason.
    UNKNOWN: safety state cannot be determined; system fails closed.
    """

    SAFE = "SAFE"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class SafetyBlockReason(StrEnum):
    """Why the Safety Authority blocked an intervention."""

    SELF_EXCLUSION = "SELF_EXCLUSION"
    PROTECTIVE_RESTRICTION = "PROTECTIVE_RESTRICTION"
    HARM_STATE = "HARM_STATE"
    UNKNOWN_SAFETY_STATE = "UNKNOWN_SAFETY_STATE"
    SAFETY_DEPENDENCY_UNAVAILABLE = "SAFETY_DEPENDENCY_UNAVAILABLE"


class NoInterventionReason(StrEnum):
    """Explicit reason codes for NO_INTERVENTION decisions.

    These distinguish why no intervention occurred, enabling audit,
    debugging, and metric tracking.
    """

    SAFETY_BLOCKED = "SAFETY_BLOCKED"
    INSUFFICIENT_CONFIDENCE = "INSUFFICIENT_CONFIDENCE"
    MISSING_AUTHORITATIVE_DATA = "MISSING_AUTHORITATIVE_DATA"
    SYSTEM_FAILURE = "SYSTEM_FAILURE"
    LEGITIMATE_RECONSIDERATION = "LEGITIMATE_RECONSIDERATION"
    NO_UNCERTAINTY_DETECTED = "NO_UNCERTAINTY_DETECTED"
    MODEL_FAILURE = "MODEL_FAILURE"
    TIMEOUT = "TIMEOUT"


class ActionId(StrEnum):
    """Registered action identifiers.

    The policy can only select from these registered actions.
    NO_INTERVENTION is always available as the safe fallback.
    """

    NO_INTERVENTION = "NO_INTERVENTION"
    EXPLAIN_MARKET = "EXPLAIN_MARKET"
    EXPLAIN_ODDS_CHANGE = "EXPLAIN_ODDS_CHANGE"
    VERIFY_SELECTIONS = "VERIFY_SELECTIONS"
    SHOW_STAKE_RETURN = "SHOW_STAKE_RETURN"
    OFFER_DEFER = "OFFER_DEFER"


class ActionCategory(StrEnum):
    """Semantic categories for actions."""

    NO_ACTION = "NO_ACTION"
    INFORMATIONAL = "INFORMATIONAL"
    VERIFICATION = "VERIFICATION"
    DEFERRAL = "DEFERRAL"


class EventType(StrEnum):
    """Types of client events the system processes."""

    SESSION_START = "SESSION_START"
    SLIP_CREATED = "SLIP_CREATED"
    CONFIRM_ATTEMPT = "CONFIRM_ATTEMPT"
    SELECTION_CHANGE = "SELECTION_CHANGE"
    ODDS_UPDATE = "ODDS_UPDATE"
    STAKE_CHANGE = "STAKE_CHANGE"
    NAVIGATION_BACK = "NAVIGATION_BACK"
    HESITATION_DETECTED = "HESITATION_DETECTED"
    SESSION_END = "SESSION_END"


class OutcomeType(StrEnum):
    """Types of outcomes following a decision."""

    CLARIFICATION_ACCEPTED = "CLARIFICATION_ACCEPTED"
    CLARIFICATION_DISMISSED = "CLARIFICATION_DISMISSED"
    BET_COMPLETED = "BET_COMPLETED"
    BET_ABANDONED = "BET_ABANDONED"
    BET_DEFERRED = "BET_DEFERRED"
    SELECTION_CORRECTED = "SELECTION_CORRECTED"
