"""Authentication endpoints for SCFCA backend (PoC).

Important: demo-safe only.
- No real password verification.
- Stores only username + role in cookies.
- Never returns password or credential-like data.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.auth.dependencies import Principal, get_current_principal
from backend.auth.schemas import LoginRequest, Role

router = APIRouter()


@router.post("/login", summary="User login", tags=["auth"])
def login(payload: LoginRequest, response: Response):
    username = (payload.username or "").strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")

    # Demo-only: we accept any non-empty password, but never store/return it.
    if not (payload.password or "").strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required")

    role: Role = payload.role

    response.set_cookie(
        key="scfca_user",
        value=username,
        httponly=True,
        samesite="lax",
    )
    response.set_cookie(
        key="scfca_role",
        value=role.value,
        httponly=True,
        samesite="lax",
    )

    return {"username": username, "role": role.value, "token": "demo-token"}


@router.post("/logout", summary="Logout", tags=["auth"])
def logout(response: Response):
    response.delete_cookie("scfca_user")
    response.delete_cookie("scfca_role")
    return {"message": "Logged out"}


@router.get("/me", summary="Current principal", tags=["auth"])
def me(principal: Principal = Depends(get_current_principal)):
    return {"username": principal.username, "role": principal.role.value}
