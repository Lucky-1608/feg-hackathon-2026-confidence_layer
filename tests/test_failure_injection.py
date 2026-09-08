"""Failure Injection Tests."""

from uuid import uuid4

import pytest

from confidence.demo.providers import DummySafetyProvider


@pytest.mark.asyncio
async def test_simulated_safety_failure() -> None:
    provider = DummySafetyProvider()
    with pytest.raises(RuntimeError, match="Simulated Safety Service Failure"):
        await provider.get_safety_context(uuid4(), "actor-safety-down")
