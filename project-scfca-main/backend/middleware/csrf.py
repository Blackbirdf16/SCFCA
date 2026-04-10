"""CSRF protection middleware for cookie-authenticated requests.

SR-18: Because authentication uses cookies, state-changing endpoints must be protected
against cross-site request forgery.

Implementation: double-submit cookie.
- Backend sets a readable CSRF cookie (non-HttpOnly).
- Client must echo the value in X-CSRF-Token header for unsafe methods.

Security notes:
- This is intentionally minimal and lightweight for the thesis PoC.
- In production, also consider Origin/Referer validation and stricter SameSite policy.
"""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.config import settings


_UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only enforce CSRF when cookie-auth is being used.
        has_auth_cookie = bool(request.cookies.get(settings.auth_cookie_name))
        if not has_auth_cookie:
            return await call_next(request)

        if request.method.upper() not in _UNSAFE_METHODS:
            return await call_next(request)

        path = request.url.path
        # Allow establishing a session.
        if path.endswith("/api/v1/auth/login"):
            return await call_next(request)

        # Allow logout without CSRF header to reduce lock-out risk.
        if path.endswith("/api/v1/auth/logout"):
            return await call_next(request)

        cookie_token = request.cookies.get(settings.csrf_cookie_name)
        header_token = request.headers.get("x-csrf-token")

        if not cookie_token or not header_token or cookie_token != header_token:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF validation failed"},
            )

        return await call_next(request)
