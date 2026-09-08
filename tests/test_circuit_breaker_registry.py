from unittest.mock import AsyncMock

import pytest

from confidence.infrastructure.resilience import CircuitBreakerRegistry, ResilienceConfig, execute_with_resilience


async def test_accumulation_and_recovery():
    CircuitBreakerRegistry.reset_all()
    breaker = CircuitBreakerRegistry.get("test", failure_threshold=2, recovery_timeout=0)
    for _ in range(2):
        with pytest.raises(ValueError):
            await execute_with_resilience(
                AsyncMock(side_effect=ValueError()), ResilienceConfig(retries=0, circuit_breaker=CircuitBreakerRegistry.get("test"))
            )
    assert breaker.state == "OPEN"
    assert breaker.can_execute()
    assert not breaker.can_execute()
    breaker.record_success()
    assert breaker.state == "CLOSED"
    CircuitBreakerRegistry.reset_all()
