import os

with open("src/confidence/infrastructure/backpressure.py", "w") as f:
    f.write('''"""Backpressure and rate limiting mechanisms."""

import asyncio

class ConcurrencyLimiter:
    """Limits concurrent execution to prevent overwhelming downstream services."""
    def __init__(self, max_concurrent: int) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self) -> None:
        await self.semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: # type: ignore
        self.semaphore.release()
''')

with open("src/confidence/application/replay.py", "w") as f:
    f.write('''"""Event replay mechanism."""

class ReplayManager:
    """Replays events from Kafka into the decision engine."""
    def __init__(self) -> None:
        self.replaying = False
        
    def start_replay(self, start_offset: int) -> None:
        self.replaying = True
        # In real app, spawn background task to seek and consume
        
    def stop_replay(self) -> None:
        self.replaying = False
''')

# Update app.py to implement graceful shutdown
with open("src/confidence/api/app.py", "r") as f:
    app = f.read()

app = app.replace(
    "    yield",
    "    yield\n    # Graceful shutdown\n    engine = _engine_cache.get('engine')\n    if engine:\n        await engine.dispose()\n    publisher = _publisher_cache.get('publisher')\n    if publisher:\n        await publisher.stop()\n"
)
app = app.replace("from fastapi import FastAPI", "from fastapi import FastAPI\nfrom confidence.api.dependencies import _engine_cache, _publisher_cache")

with open("src/confidence/api/app.py", "w") as f:
    f.write(app)

