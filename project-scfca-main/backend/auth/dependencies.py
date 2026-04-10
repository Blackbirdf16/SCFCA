"""Authentication + RBAC dependencies for SCFCA PoC.

Demo-safe only:
- Uses cookies (or optional headers) to identify a principal.
- No password verification and no database dependency.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status

from backend.auth.jwt import decode_access_token
from backend.auth.schemas import Role
from backend.core.config import settings
from backend.services.session_store import SESSION_STORE


@dataclass(frozen=True)
class Principal:
    username: str
    role: Role


def _get_token_from_request(request: Request) -> str | None:
    token = request.cookies.get(settings.auth_cookie_name)
    if token:
        return token

    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip() or None

    return None


def _principal_from_token(token: str) -> Principal:
    payload = decode_access_token(
        token=token,
        secret_key=settings.secret_key,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )
    jti = str(payload.get("jti") or "")
    if not jti or SESSION_STORE.is_revoked(jti):
        raise ValueError("Token revoked")
    username = str(payload.get("sub") or "")
    role_raw = str(payload.get("role") or "")
    if not username:
        raise ValueError("Missing sub")
    return Principal(username=username, role=Role(role_raw))


def _principal_from_legacy_request(request: Request) -> Principal | None:
    username = request.cookies.get("scfca_user") or request.headers.get("x-scfca-user")
    role_raw = request.cookies.get("scfca_role") or request.headers.get("x-scfca-role")
    if not (username and role_raw):
        return None
    try:
        return Principal(username=username, role=Role(role_raw))
    except ValueError:
        return None


def get_current_principal(request: Request) -> Principal:
    token = _get_token_from_request(request)
    if token:
        try:
            return _principal_from_token(token)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if settings.allow_legacy_auth and settings.debug:
        principal = _principal_from_legacy_request(request)
        if principal:
            return principal

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def require_any_role(roles: list[Role]):
    def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if principal.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}",
            )
        return principal

    return dependency


def require_role(role: Role):
    return require_any_role([role])


def get_optional_principal(request: Request) -> Principal | None:
    try:
        return get_current_principal(request)
    except HTTPException:
        return None
