"""General API rate limiting middleware for SCFCA.

MU-9: Denial of service mitigation.

Applies per-IP rate limits to all API endpoints.
- Read endpoints (GET/HEAD/OPTIONS): 120 req/min
- Write endpoints (POST/PUT/PATCH/DELETE): 60 req/min

Login has its own stricter limiter (8/60s) in the auth route.
This middleware provides a broad safety net for all other endpoints.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.services.rate_limit import SlidingWindowRateLimiter

_WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Separate limiters for read vs write
_read_limiter = SlidingWindowRateLimiter(max_attempts=120, window_seconds=60)
_write_limiter = SlidingWindowRateLimiter(max_attempts=60, window_seconds=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global per-IP rate limiting. MU-9 mitigation."""

    async def dispatch(self, request: Request, call_next):
        # Skip health checks
        if request.url.path == "/api/v1/health/" or request.url.path == "/api/v1/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        if request.method in _WRITE_METHODS:
            result = _write_limiter.check(f"write:{client_ip}")
        else:
            result = _read_limiter.check(f"read:{client_ip}")

        if not result.allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Try again later."},
                headers={"Retry-After": str(result.retry_after_seconds)},
            )

        response = await call_next(request)
        return response
