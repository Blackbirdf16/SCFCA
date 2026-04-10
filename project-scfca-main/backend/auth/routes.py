"""Authentication API routes for SCFCA PoC.

Implements a lightweight but real authentication flow:
- Demo users stored in-memory
- Passwords verified with bcrypt
- Signed JWT access token issued in an HttpOnly cookie
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from passlib.context import CryptContext

from backend.auth.dependencies import get_current_principal
from backend.auth.jwt import create_access_token
from backend.auth.schemas import LoginRequest, LoginResponse, MeResponse, Role
from backend.core.config import settings

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Demo users (PoC-only). Roles are authoritative here.
_DEMO_USERS: dict[str, dict[str, str]] = {
    "alice": {"password_hash": pwd_context.hash("alice123"), "role": Role.regular.value},
    "bob": {"password_hash": pwd_context.hash("bob123"), "role": Role.administrator.value},
    "eve": {"password_hash": pwd_context.hash("eve123"), "role": Role.administrator.value},
    "carol": {"password_hash": pwd_context.hash("carol123"), "role": Role.auditor.value},
}


def _authenticate(username: str, password: str) -> tuple[str, Role] | None:
    record = _DEMO_USERS.get((username or "").strip().lower())
    if not record:
        return None

    if not pwd_context.verify(password or "", record["password_hash"]):
        return None

    return username.strip().lower(), Role(record["role"])

@router.post("/login", summary="User login")
def login(request: LoginRequest, response: Response) -> LoginResponse:
    username = (request.username or "").strip().lower()
    password = request.password or ""

    authenticated = _authenticate(username, password)
    if not authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    auth_username, role = authenticated

    token = create_access_token(
        subject=auth_username,
        role=role.value,
        secret_key=settings.secret_key,
        expires_minutes=60,
    )

    response.set_cookie(
        key="scfca_access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60,
        path="/",
    )

    return LoginResponse(username=auth_username, role=role)


@router.post("/logout", summary="User logout")
def logout(response: Response):
    response.delete_cookie(key="scfca_access_token", path="/")
    return {"status": "ok"}


@router.get("/me", summary="Current user")
def me(principal=Depends(get_current_principal)) -> MeResponse:
    return MeResponse(username=principal.username, role=principal.role)
