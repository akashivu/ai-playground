from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass
class _CacheEntry(Generic[T]):
    value: T
    expires_at: float


class PlaceCacheService(Generic[T]):
    """Async, single-flight, size-bounded TTL cache for provider responses.

    Single-flight: concurrent callers for the same uncached key share
    one in-flight fetch instead of each triggering their own paid API
    call. Without this, a cold key under concurrent load fans out into
    N identical Google requests instead of 1.

    Process-local by design — isolated behind this class so it can be
    swapped for Redis later without touching DestinationPlacesService.
    """

    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 500) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero")
        if max_entries <= 0:
            raise ValueError("max_entries must be greater than zero")

        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries

        self._entries: dict[str, _CacheEntry[T]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _get_fresh(self, key: str) -> T | None:
        entry = self._entries.get(key)
        if entry is None:
            return None

        if entry.expires_at <= time.monotonic():
            self._entries.pop(key, None)
            self._locks.pop(key, None)
            return None

        return entry.value

    def _set(self, key: str, value: T) -> None:
        if len(self._entries) >= self._max_entries and key not in self._entries:
            self._evict_oldest_expiring()

        self._entries[key] = _CacheEntry(
            value=value,
            expires_at=time.monotonic() + self._ttl_seconds,
        )

    def _evict_oldest_expiring(self) -> None:
        if not self._entries:
            return
        oldest_key = min(self._entries, key=lambda k: self._entries[k].expires_at)
        self._entries.pop(oldest_key, None)
        self._locks.pop(oldest_key, None)

    async def get_or_set(self, key: str, factory: Callable[[], Awaitable[T]]) -> T:
        cached = self._get_fresh(key)
        if cached is not None:
            return cached

        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            # Another caller may have populated this while we waited.
            cached = self._get_fresh(key)
            if cached is not None:
                return cached

            value = await factory()
            self._set(key, value)
            return value

    def delete(self, key: str) -> None:
        self._entries.pop(key, None)
        self._locks.pop(key, None)

    def clear(self) -> None:
        self._entries.clear()
        self._locks.clear()