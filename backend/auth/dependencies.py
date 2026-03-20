"""Authentication + RBAC dependencies for SCFCA PoC.

Demo-safe only:
- Uses cookies (or optional headers) to identify a principal.
- No password verification and no database dependency.
"""

from dataclasses import dataclass
from fastapi import Depends, HTTPException, Request, status

from backend.auth.schemas import Role


@dataclass(frozen=True)
class Principal:
    username: str
    role: Role


def get_current_principal(request: Request) -> Principal:
    username = request.cookies.get("scfca_user") or request.headers.get("x-scfca-user")
    role_raw = request.cookies.get("scfca_role") or request.headers.get("x-scfca-role")

    if not username or not role_raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        role = Role(role_raw)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role") from exc

    return Principal(username=username, role=role)


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
