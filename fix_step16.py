import os

os.makedirs("src/confidence/demo", exist_ok=True)
with open("src/confidence/demo/__init__.py", "w") as f:
    f.write('"""Demo package for synthetic implementations."""\n')

with open("src/confidence/demo/providers.py", "w") as f:
    f.write('''"""Synthetic providers for demo purposes."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from confidence.domain.models import (
    HarmIndicators,
    MarketContext,
    OddsSnapshot,
    SafetyContext,
    Selection,
    SlipContext,
)
from confidence.domain.ports import MarketProvider, SafetyProvider, SlipProvider

class DummySafetyProvider(SafetyProvider):
    """Synthetic safety provider for demo scenarios."""

    async def get_safety_context(self, session_id: UUID, anonymous_actor_id: str) -> SafetyContext:
        if anonymous_actor_id == "actor-safety-down":
            raise RuntimeError("Simulated Safety Service Failure")

        harm = HarmIndicators(rapid_loss_chasing=(anonymous_actor_id == "actor-harm"))
        is_excluded = anonymous_actor_id == "actor-self-excluded"

        return SafetyContext(
            is_self_excluded=is_excluded,
            harm_indicators=harm,
            data_freshness=datetime.now(UTC),
        )


class DummySlipProvider(SlipProvider):
    """Synthetic slip provider for demo scenarios."""

    async def get_slip_context(self, slip_id: str) -> SlipContext:
        if slip_id == "slip-down":
            raise RuntimeError("Simulated Slip Service Failure")

        odds_hist = []
        if slip_id != "slip-missing-odds":
            odds_hist = [
                OddsSnapshot(
                    odds=Decimal("2.30"),
                    timestamp=datetime.now(UTC),
                    source="test",
                )
            ]

        return SlipContext(
            slip_id=slip_id,
            selections=[
                Selection(
                    selection_id="sel-1",
                    market_id="mkt-1",
                    event_id="evt-1",
                    event_name="Demo Match",
                    market_name="Match Winner",
                    odds=Decimal("2.5"),
                    odds_history=odds_hist,
                )
            ],
            stake=Decimal("10.0"),
            potential_return=Decimal("25.0"),
            created_at=datetime.now(UTC),
        )


class DummyMarketProvider(MarketProvider):
    """Synthetic market provider for demo scenarios."""

    async def get_market_context(self, market_id: str) -> MarketContext:
        return MarketContext(
            market_id=market_id,
            market_name="Match Winner",
            event_name="Demo Match",
            market_definition="Predict the winner.",
            data_freshness=datetime.now(UTC),
        )
''')

with open("src/confidence/api/dependencies.py", "r") as f:
    deps = f.read()

deps = deps.replace(
    "from confidence.domain.ports import MarketProvider, PersistenceProvider, SafetyProvider, SlipProvider",
    "from confidence.domain.ports import PersistenceProvider\nfrom confidence.demo.providers import DummySafetyProvider, DummySlipProvider, DummyMarketProvider"
)

# Remove the classes from dependencies.py
import re
deps = re.sub(r'class DummySafetyProvider.*?class DummySlipProvider.*?class DummyMarketProvider.*?def get_engine', 'def get_engine', deps, flags=re.DOTALL)

with open("src/confidence/api/dependencies.py", "w") as f:
    f.write(deps)

