"""Resilience patterns.

Implements timeouts, circuit breakers, and retries for external dependencies.
"""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar

from confidence.log import get_logger
from confidence.observability.metrics import CIRCUIT_STATE, PROVIDER_ERRORS, PROVIDER_LATENCY

logger = get_logger("confidence.resilience")


class CircuitBreaker:
    """A simple async circuit breaker."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
        self.name = "unknown"
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time: float | None = None

    def record_failure(self) -> None:
        """Record a failure."""
        self.failures += 1
        self.last_failure_time = asyncio.get_running_loop().time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("circuit_breaker_opened")

    def record_success(self) -> None:
        """Record a success and reset if half-open."""
        if self.state == "HALF-OPEN":
            self.state = "CLOSED"
            logger.info("circuit_breaker_closed")
        self.failures = 0

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            now = asyncio.get_running_loop().time()
            if self.last_failure_time and (now - self.last_failure_time) > self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("circuit_breaker_half_open")
                return True
            return False
        # Only the caller that transitioned OPEN -> HALF-OPEN owns the probe.
        return False


class ResilienceConfig:
    """Configuration for resilience strategies."""

    def __init__(self, timeout_seconds: float = 1.0, retries: int = 2, circuit_breaker: CircuitBreaker | None = None) -> None:
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.circuit_breaker = circuit_breaker or CircuitBreaker()


async def execute_with_resilience[T](
    func: Callable[..., Awaitable[T]],
    config: ResilienceConfig,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute a function with timeout, retries, and circuit breaker."""
    if not config.circuit_breaker.can_execute():
        raise RuntimeError("Circuit breaker is OPEN")

    started = time.monotonic()
    last_error: Exception | None = None
    for attempt in range(config.retries + 1):
        try:
            async with asyncio.timeout(config.timeout_seconds):
                result = await func(*args, **kwargs)
                config.circuit_breaker.record_success()
                PROVIDER_LATENCY.labels(provider=config.circuit_breaker.name).observe(time.monotonic() - started)
                CIRCUIT_STATE.labels(service=config.circuit_breaker.name).set(0)
                return result
        except TimeoutError as e:
            last_error = e
            logger.warning("timeout_occurred", attempt=attempt)
        except Exception as e:
            last_error = e
            logger.warning("execution_failed", error=str(e), attempt=attempt)

        if attempt < config.retries:
            await asyncio.sleep(random.uniform(0.005, 0.01) * 2**attempt)

    PROVIDER_ERRORS.labels(provider=config.circuit_breaker.name).inc()
    config.circuit_breaker.record_failure()
    CIRCUIT_STATE.labels(service=config.circuit_breaker.name).set(2 if config.circuit_breaker.state == "OPEN" else 0)
    raise last_error or RuntimeError("Max retries exceeded")


class CircuitBreakerRegistry:
    """Share dependency failure history across requests."""

    _breakers: ClassVar[dict[str, CircuitBreaker]] = {}

    @classmethod
    def get(cls, name: str, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> CircuitBreaker:
        if name not in cls._breakers:
            cls._breakers[name] = CircuitBreaker(failure_threshold, recovery_timeout)
            cls._breakers[name].name = name
        return cls._breakers[name]

    @classmethod
    def reset_all(cls) -> None:
        cls._breakers.clear()
