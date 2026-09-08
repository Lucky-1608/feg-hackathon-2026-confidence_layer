"""Backpressure and rate limiting mechanisms."""

import asyncio


class ConcurrencyLimiter:
    """Limits concurrent execution to prevent overwhelming downstream services."""

    def __init__(self, max_concurrent: int) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self) -> None:
        await self.semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        self.semaphore.release()
