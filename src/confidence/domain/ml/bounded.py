"""One bounded inference slot: a stuck model cannot create an unbounded queue."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any


class BoundedInference:
    def __init__(self, timeout_seconds: float = 0.02) -> None:
        self.timeout = timeout_seconds
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="model")
        self.slot = Lock()

    def run(self, function: Callable[[], Any]) -> Any:
        if not self.slot.acquire(blocking=False):
            raise TimeoutError("Model busy")
        try:
            future = self.pool.submit(function)
        except Exception:
            self.slot.release()
            raise
        future.add_done_callback(lambda _: self.slot.release())
        return future.result(timeout=self.timeout)

    def close(self) -> None:
        self.pool.shutdown(wait=False, cancel_futures=True)
