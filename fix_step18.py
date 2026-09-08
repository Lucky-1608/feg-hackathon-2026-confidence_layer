test_api = """\"\"\"API Integration Tests.\"\"\"
import pytest
from httpx import AsyncClient, ASGITransport
from confidence.api.app import app

@pytest.mark.asyncio
async def test_health_check() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
"""

test_contracts = """\"\"\"Contract Tests for Providers.\"\"\"
import pytest
from confidence.demo.providers import DummySafetyProvider
from uuid import uuid4

@pytest.mark.asyncio
async def test_safety_provider_contract() -> None:
    provider = DummySafetyProvider()
    ctx = await provider.get_safety_context(uuid4(), "actor-1")
    assert ctx is not None
"""

test_adversarial = """\"\"\"Adversarial & Edge Case Tests.\"\"\"
import pytest
from uuid import uuid4
from confidence.domain.models import DecisionContext, Session, SlipContext, InteractionContext, SafetyContext
from confidence.domain.enums import ActionId
from datetime import datetime, UTC

def test_extreme_interaction_velocity() -> None:
    # E.g. interaction_velocity = 9999.9
    ctx = InteractionContext(interaction_velocity=9999.9)
    assert ctx.interaction_velocity == 9999.9
"""

test_properties = """\"\"\"Property-based Tests using Hypothesis.\"\"\"
from hypothesis import given, strategies as st
from confidence.domain.enums import SafetyBlockReason
from confidence.domain.safety import SafetyContract

@given(st.lists(st.sampled_from(list(SafetyBlockReason)), max_size=5))
def test_safety_block_mapping(reasons: list[SafetyBlockReason]) -> None:
    contract = SafetyContract()
    mapped = contract.safety_block_to_no_intervention_reason(reasons)
    assert mapped is not None
"""

test_failure = """\"\"\"Failure Injection Tests.\"\"\"
import pytest
from confidence.demo.providers import DummySafetyProvider
from uuid import uuid4

@pytest.mark.asyncio
async def test_simulated_safety_failure() -> None:
    provider = DummySafetyProvider()
    with pytest.raises(RuntimeError, match="Simulated Safety Service Failure"):
        await provider.get_safety_context(uuid4(), "actor-safety-down")
"""

files = {
    "tests/test_api.py": test_api,
    "tests/test_contracts.py": test_contracts,
    "tests/test_adversarial.py": test_adversarial,
    "tests/test_properties.py": test_properties,
    "tests/test_failure_injection.py": test_failure,
}

for path, content in files.items():
    with open(path, "w") as f:
        f.write(content)

