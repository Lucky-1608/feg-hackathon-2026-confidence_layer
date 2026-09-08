"""Tests for resilience patterns."""

import asyncio

import pytest

from confidence.infrastructure.resilience import CircuitBreaker, ResilienceConfig, execute_with_resilience


@pytest.mark.asyncio
async def test_circuit_breaker_transitions() -> None:
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    assert cb.can_execute() is True

    cb.record_failure()
    assert cb.can_execute() is True

    cb.record_failure()
    assert cb.can_execute() is False
    assert cb.state == "OPEN"

    # Wait for recovery
    await asyncio.sleep(0.15)

    assert cb.can_execute() is True
    assert cb.state == "HALF-OPEN"

    cb.record_success()
    assert cb.state == "CLOSED"


@pytest.mark.asyncio
async def test_execute_with_resilience_success() -> None:
    config = ResilienceConfig(timeout_seconds=0.1, retries=1)

    async def dummy() -> str:
        return "success"

    result = await execute_with_resilience(dummy, config)
    assert result == "success"


@pytest.mark.asyncio
async def test_execute_with_resilience_timeout() -> None:
    config = ResilienceConfig(timeout_seconds=0.01, retries=1)

    async def slow() -> str:
        await asyncio.sleep(0.05)
        return "success"

    with pytest.raises(TimeoutError):
        await execute_with_resilience(slow, config)

    assert config.circuit_breaker.failures == 1
