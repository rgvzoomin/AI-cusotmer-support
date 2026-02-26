from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock


class InMemoryRateLimiter:
    """Per-client sliding window rate limiter."""

    def __init__(self, limit_per_minute: int = 120) -> None:
        self.limit = limit_per_minute
        self.window_seconds = 60
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, client_id: str) -> bool:
        now = time.time()
        with self._lock:
            q = self._requests[client_id]
            while q and (now - q[0]) > self.window_seconds:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True
