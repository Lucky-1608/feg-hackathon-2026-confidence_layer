"""Contract Tests for Providers."""

from uuid import uuid4

import pytest

from confidence.demo.providers import DummySafetyProvider


@pytest.mark.asyncio
async def test_safety_provider_contract() -> None:
    provider = DummySafetyProvider()
    ctx = await provider.get_safety_context(uuid4(), "actor-1")
    assert ctx is not None
