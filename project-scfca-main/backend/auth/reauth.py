"""Re-authentication dependency for sensitive actions.

SR-6: The system shall require explicit re-authentication before
executing custody-impacting actions.

Usage:
    @router.post("/execute")
    def execute(principal = Depends(get_current_principal), _ = Depends(require_reauth)):
        ...

The client must obtain a short-lived reauth token via POST /api/v1/auth/reauth
and pass it in the X-Reauth-Token header.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from backend.auth.jwt import decode_access_token
from backend.core.config import settings


def require_reauth(request: Request) -> None:
    """Validate the X-Reauth-Token header.

    Raises 403 if the token is missing, expired, or not a reauth token.
    Can be used as a FastAPI Depends() or called directly.
    """
    validate_reauth_token(request)


def validate_reauth_token(request: Request) -> None:
    """Validate reauth token from request headers. SR-6.

    Call this from within route bodies when reauth should only apply
    conditionally (e.g., only on the DB path, not the legacy fallback).
    """
    token = request.headers.get("X-Reauth-Token") or request.headers.get("x-reauth-token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Re-authentication required. Provide X-Reauth-Token header.",
        )

    try:
        payload = decode_access_token(
            token=token.strip(),
            secret_key=settings.secret_key,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired re-authentication token.",
        )

    if payload.get("role") != "reauth":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token is not a re-authentication token.",
        )
