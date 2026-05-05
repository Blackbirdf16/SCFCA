"""Authentication + RBAC dependencies for SCFCA PoC."""

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request, status

from backend.auth.schemas import Role
from backend.core.config import settings


@dataclass(frozen=True)
class Principal:
    username: str
    role: Role


SESSION_COOKIE = "scfca_session"


def _sign(value: str) -> str:
    return hmac.new(settings.secret_key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_cookie(username: str, role: Role) -> str:
    payload = {"username": username, "role": role.value}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii")
    return f"{encoded}.{_sign(encoded)}"


def _read_session_cookie(value: str) -> Principal:
    try:
        encoded, supplied_signature = value.rsplit(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc

    expected_signature = _sign(encoded)
    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    try:
        decoded = base64.urlsafe_b64decode(encoded.encode("ascii"))
        payload = json.loads(decoded)
        username = str(payload["username"]).strip()
        role = Role(payload["role"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc

    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    return Principal(username=username, role=role)


def get_current_principal(request: Request) -> Principal:
    session_cookie = request.cookies.get(SESSION_COOKIE)
    if not session_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return _read_session_cookie(session_cookie)


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
