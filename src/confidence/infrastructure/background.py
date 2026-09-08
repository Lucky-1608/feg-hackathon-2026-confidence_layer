"""Tracked audit tasks; shutdown waits within a fixed drain budget."""

import asyncio
from collections.abc import Coroutine
from typing import Any

from confidence.log import get_logger

pending_tasks: set[asyncio.Task[None]] = set()


def schedule(coroutine: Coroutine[Any, Any, None]) -> None:
    task = asyncio.create_task(coroutine)
    pending_tasks.add(task)
    task.add_done_callback(pending_tasks.discard)


async def drain(timeout: float = 5.0) -> tuple[int, int]:
    if not pending_tasks:
        return 0, 0
    done, pending = await asyncio.wait(set(pending_tasks), timeout=timeout)
    for task in pending:
        task.cancel()
    get_logger("confidence.shutdown").info("audit_tasks_drained", drained=len(done), abandoned=len(pending))
    return len(done), len(pending)
