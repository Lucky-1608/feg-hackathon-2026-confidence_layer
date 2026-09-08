"""Shared test fixtures for the Confidence Layer test suite."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from confidence.domain.actions import ActionRegistry
from confidence.domain.models import (
    DecisionContext,
    HarmIndicators,
    InteractionContext,
    MarketContext,
    OddsSnapshot,
    SafetyContext,
    Selection,
    Session,
    SlipContext,
)
from confidence.domain.safety import SafetyContract


@pytest.fixture
def now() -> datetime:
    """Fixed 'now' timestamp for deterministic tests."""
    return datetime(2026, 9, 3, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def session(now: datetime) -> Session:
    """A standard test session."""
    return Session(
        session_id=uuid4(),
        anonymous_actor_id="test-actor-001",
        started_at=now,
        client_version="1.0.0",
    )


@pytest.fixture
def safe_safety_context(now: datetime) -> SafetyContext:
    """Safety context with no restrictions — intervention is permitted."""
    return SafetyContext(
        is_self_excluded=False,
        has_protective_restrictions=False,
        harm_indicators=HarmIndicators(),
        data_freshness=now,
    )


@pytest.fixture
def self_excluded_safety_context(now: datetime) -> SafetyContext:
    """Safety context for a self-excluded user."""
    return SafetyContext(
        is_self_excluded=True,
        has_protective_restrictions=False,
        harm_indicators=HarmIndicators(),
        data_freshness=now,
    )


@pytest.fixture
def harm_safety_context(now: datetime) -> SafetyContext:
    """Safety context with harm indicators present."""
    return SafetyContext(
        is_self_excluded=False,
        has_protective_restrictions=False,
        harm_indicators=HarmIndicators(
            rapid_loss_chasing=True,
            escalating_stakes=True,
        ),
        data_freshness=now,
    )


@pytest.fixture
def protective_restriction_context(now: datetime) -> SafetyContext:
    """Safety context with a protective restriction."""
    return SafetyContext(
        is_self_excluded=False,
        has_protective_restrictions=True,
        harm_indicators=HarmIndicators(),
        data_freshness=now,
    )


@pytest.fixture
def stale_safety_context() -> SafetyContext:
    """Safety context with stale data (older than max age)."""
    return SafetyContext(
        is_self_excluded=False,
        has_protective_restrictions=False,
        harm_indicators=HarmIndicators(),
        data_freshness=datetime(2026, 9, 3, 11, 0, 0, tzinfo=UTC),
    )


@pytest.fixture
def no_freshness_safety_context() -> SafetyContext:
    """Safety context with no data freshness timestamp."""
    return SafetyContext(
        is_self_excluded=False,
        has_protective_restrictions=False,
        harm_indicators=HarmIndicators(),
        data_freshness=None,
    )


@pytest.fixture
def sample_slip(now: datetime) -> SlipContext:
    """A sample betslip with one selection."""
    return SlipContext(
        slip_id="slip-001",
        selections=[
            Selection(
                selection_id="sel-001",
                market_id="mkt-001",
                event_id="evt-001",
                event_name="Team A vs Team B",
                market_name="Match Result",
                odds=Decimal("2.50"),
                odds_at_placement=Decimal("2.30"),
                odds_history=[
                    OddsSnapshot(
                        odds=Decimal("2.30"),
                        timestamp=now,
                        source="authoritative",
                    ),
                ],
            ),
        ],
        stake=Decimal("10.00"),
        potential_return=Decimal("25.00"),
        created_at=now,
    )


@pytest.fixture
def sample_market(now: datetime) -> MarketContext:
    """A sample market context."""
    return MarketContext(
        market_id="mkt-001",
        market_name="Match Result",
        event_name="Team A vs Team B",
        market_definition="Bet on the final result of the match.",
        odds_history=[
            OddsSnapshot(
                odds=Decimal("2.30"),
                timestamp=now,
                source="authoritative",
            ),
        ],
        is_live=False,
        data_freshness=now,
    )


@pytest.fixture
def sample_interaction() -> InteractionContext:
    """A sample interaction context indicating hesitation."""
    return InteractionContext(
        session_age_seconds=120.0,
        recent_backtracks=1,
        dwell_time_seconds=15.0,
        selection_changes=0,
        stake_changes=0,
        odds_changed=True,
        time_since_slip_creation_seconds=60.0,
        confirmation_attempts=2,
        interaction_velocity=3.0,
    )


@pytest.fixture
def sample_context(
    session: Session,
    sample_slip: SlipContext,
    sample_market: MarketContext,
    safe_safety_context: SafetyContext,
    sample_interaction: InteractionContext,
) -> DecisionContext:
    """A complete decision context for testing."""
    return DecisionContext(
        session=session,
        slip=sample_slip,
        markets=[sample_market],
        safety=safe_safety_context,
        interaction=sample_interaction,
    )


@pytest.fixture
def action_registry() -> ActionRegistry:
    """The default action registry."""
    return ActionRegistry()


@pytest.fixture
def safety_contract() -> SafetyContract:
    """The default safety contract."""
    return SafetyContract()


@pytest.fixture(autouse=True)
def isolated_rate_limits(monkeypatch):
    # Unit API transports deliberately omit app lifespan; rate middleware has dedicated integration tests.
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
