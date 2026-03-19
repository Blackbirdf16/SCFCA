"""
Authentication and RBAC dependencies for SCFCA PoC.
Not production-grade: demo only.
"""
from fastapi import Depends, HTTPException, status, Request
from backend.core.models import User, RoleEnum
from backend.core.database import SessionLocal
from typing import Optional

# Simple session-based demo auth (not secure, for PoC only)

def get_current_user(request: Request) -> User:
    username = request.cookies.get("scfca_user")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_role(role: RoleEnum):
    def dependency(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires role: {role}")
        return user
    return dependency

def require_any_role(roles: list[RoleEnum]):
    def dependency(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires one of roles: {roles}")
        return user
    return dependency
