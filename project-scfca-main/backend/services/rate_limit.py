"""Lightweight in-memory rate limiting (PoC).

SR-19: brute-force resistance for login.

This is intentionally simple (process-local) and should be replaced with a shared
store (Redis) in production deployments.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class SlidingWindowRateLimiter:
    def __init__(self, *, max_attempts: int, window_seconds: int) -> None:
        self._max_attempts = max(1, int(max_attempts))
        self._window = max(1, int(window_seconds))
        self._lock = threading.Lock()
        self._events: dict[str, list[float]] = {}

    def check(self, key: str) -> RateLimitResult:
        now = time.time()
        cutoff = now - self._window

        with self._lock:
            events = self._events.get(key, [])
            events = [t for t in events if t >= cutoff]

            if len(events) >= self._max_attempts:
                oldest = min(events)
                retry_after = max(1, int((oldest + self._window) - now))
                self._events[key] = events
                return RateLimitResult(allowed=False, remaining=0, retry_after_seconds=retry_after)

            events.append(now)
            self._events[key] = events
            remaining = self._max_attempts - len(events)
            return RateLimitResult(allowed=True, remaining=remaining, retry_after_seconds=0)


LOGIN_RATE_LIMITER: SlidingWindowRateLimiter | None = None


def get_login_rate_limiter(*, max_attempts: int, window_seconds: int) -> SlidingWindowRateLimiter:
    global LOGIN_RATE_LIMITER
    if LOGIN_RATE_LIMITER is None:
        LOGIN_RATE_LIMITER = SlidingWindowRateLimiter(max_attempts=max_attempts, window_seconds=window_seconds)
    return LOGIN_RATE_LIMITER
