"""CSRF helpers for cookie-authenticated state-changing requests."""

import secrets

from fastapi import HTTPException, Request, status

CSRF_COOKIE = "scfca_csrf"
CSRF_HEADER = "x-csrf-token"


def create_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def require_csrf(request: Request) -> None:
    cookie_token = request.cookies.get(CSRF_COOKIE)
    header_token = request.headers.get(CSRF_HEADER)

    if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token missing or invalid")
