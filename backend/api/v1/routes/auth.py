"""Authentication endpoints for SCFCA backend (PoC).

Important: demo-safe only.
- Uses a fixed local demo credential map.
- Stores signed session metadata in an HttpOnly cookie.
- Never returns password or credential-like data.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.auth.csrf import CSRF_COOKIE, create_csrf_token, require_csrf
from backend.auth.dependencies import SESSION_COOKIE, Principal, create_session_cookie, get_current_principal
from backend.auth.schemas import LoginRequest, Role

router = APIRouter()

DEMO_USERS: dict[str, tuple[str, Role]] = {
    "alice": ("alice123", Role.regular),
    "bob": ("bob123", Role.administrator),
    "eve": ("eve123", Role.administrator),
    "carol": ("carol123", Role.auditor),
    "ops_team": ("ops123", Role.regular),
    "admin_team": ("admin123", Role.administrator),
}


@router.post("/login", summary="User login", tags=["auth"])
def login(payload: LoginRequest, response: Response):
    username = (payload.username or "").strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")

    # Demo-only: we accept any non-empty password, but never store/return it.
    if not (payload.password or "").strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required")

    demo_user = DEMO_USERS.get(username)
    if demo_user is None or payload.password != demo_user[0]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    role = demo_user[1]
    if payload.role is not None and payload.role != role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role does not match demo credential")

    csrf_token = create_csrf_token()

    response.set_cookie(
        key=SESSION_COOKIE,
        value=create_session_cookie(username, role),
        httponly=True,
        samesite="lax",
    )
    response.set_cookie(
        key=CSRF_COOKIE,
        value=csrf_token,
        httponly=False,
        samesite="lax",
    )

    return {"username": username, "role": role.value, "csrfToken": csrf_token}


@router.post("/logout", summary="Logout", tags=["auth"])
def logout(response: Response, _: None = Depends(require_csrf)):
    response.delete_cookie(SESSION_COOKIE)
    response.delete_cookie(CSRF_COOKIE)
    return {"message": "Logged out"}


@router.get("/me", summary="Current principal", tags=["auth"])
def me(principal: Principal = Depends(get_current_principal)):
    return {"username": principal.username, "role": principal.role.value}
