"""Resilience patterns.

Implements timeouts, circuit breakers, and retries for external dependencies.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from confidence.log import get_logger

logger = get_logger("confidence.resilience")

T = TypeVar("T")


class CircuitBreaker:
    """A simple async circuit breaker."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
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
        # HALF-OPEN
        return True


class ResilienceConfig:
    """Configuration for resilience strategies."""

    def __init__(self, timeout_seconds: float = 1.0, retries: int = 2) -> None:
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.circuit_breaker = CircuitBreaker()


async def execute_with_resilience[T](
    func: Callable[..., Awaitable[T]],
    config: ResilienceConfig,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute a function with timeout, retries, and circuit breaker."""
    if not config.circuit_breaker.can_execute():
        raise RuntimeError("Circuit breaker is OPEN")

    last_error: Exception | None = None
    for attempt in range(config.retries + 1):
        try:
            async with asyncio.timeout(config.timeout_seconds):
                result = await func(*args, **kwargs)
                config.circuit_breaker.record_success()
                return result
        except TimeoutError as e:
            last_error = e
            logger.warning("timeout_occurred", attempt=attempt)
        except Exception as e:
            last_error = e
            logger.warning("execution_failed", error=str(e), attempt=attempt)

    config.circuit_breaker.record_failure()
    raise last_error or RuntimeError("Max retries exceeded")
