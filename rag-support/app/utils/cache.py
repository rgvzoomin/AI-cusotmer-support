from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from typing import Generic, TypeVar

T = TypeVar('T')


@dataclass
class CacheItem(Generic[T]):
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    """Simple thread-safe LRU cache with TTL."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 600) -> None:
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, CacheItem[T]] = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> T | None:
        now = time.time()
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            if item.expires_at < now:
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)
            return item.value

    def set(self, key: str, value: T) -> None:
        with self._lock:
            if key in self._store:
                self._store.pop(key)
            self._store[key] = CacheItem(value=value, expires_at=time.time() + self.ttl_seconds)
            while len(self._store) > self.max_size:
                self._store.popitem(last=False)
