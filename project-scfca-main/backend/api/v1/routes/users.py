"""User management endpoints for SCFCA.

FR-1: Administrators can create and manage user profiles.
SR-4: Controlled role assignment — role changes are restricted and fully logged.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import Principal, get_current_principal, require_role
from backend.auth.schemas import Role
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import get_password_hash
from backend.repositories.user_repo import USER_REPO
from backend.repositories.audit_repo import AUDIT_REPO
from backend.services.security_ids import pseudonymous_actor_id
from backend.users.schemas import UserCreate, UserRead, UserRoleUpdate

router = APIRouter()

AdminOnly = Annotated[Principal, Depends(require_role(Role.administrator))]


@router.post("/", summary="Create user", response_model=UserRead, tags=["users"])
def create_user(
    payload: UserCreate,
    principal: AdminOnly,
    db: Session = Depends(get_db),
) -> UserRead:
    """Create a new user account. Admin only. [FR-1, SR-4]"""
    existing = USER_REPO.get_by_username(db, payload.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    user = USER_REPO.create(
        db,
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        created_by=None,  # Will be linked after we look up principal's UUID
    )

    AUDIT_REPO.append(
        db,
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="admin",
        action="user_created",
        entity_type="user",
        entity_id=user.username,
        details={"role": payload.role.value, "created_by": principal.username},
    )

    return UserRead.model_validate(user)


@router.get("/", summary="List users", response_model=list[UserRead], tags=["users"])
def list_users(
    principal: AdminOnly,
    db: Session = Depends(get_db),
) -> list[UserRead]:
    """List all active users. Admin only. [FR-1]"""
    users = USER_REPO.list_all(db, active_only=True)
    return [UserRead.model_validate(u) for u in users]


@router.patch("/{user_id}/role", summary="Change user role", response_model=UserRead, tags=["users"])
def change_role(
    user_id: UUID,
    payload: UserRoleUpdate,
    principal: AdminOnly,
    db: Session = Depends(get_db),
) -> UserRead:
    """Change a user's role. Admin only, fully logged. [SR-4]"""
    user = USER_REPO.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_role = user.role.value
    updated = USER_REPO.update_role(db, user_id, payload.role)

    AUDIT_REPO.append(
        db,
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="admin",
        action="role_changed",
        entity_type="user",
        entity_id=user.username,
        details={"old_role": old_role, "new_role": payload.role.value, "changed_by": principal.username},
    )

    return UserRead.model_validate(updated)


@router.delete("/{user_id}", summary="Deactivate user", response_model=UserRead, tags=["users"])
def deactivate_user(
    user_id: UUID,
    principal: AdminOnly,
    db: Session = Depends(get_db),
) -> UserRead:
    """Deactivate a user account (soft delete). Admin only. [FR-1]"""
    user = USER_REPO.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if str(user.id) == str(principal.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    deactivated = USER_REPO.deactivate(db, user_id)

    AUDIT_REPO.append(
        db,
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="admin",
        action="user_deactivated",
        entity_type="user",
        entity_id=user.username,
        details={"deactivated_by": principal.username},
    )

    return UserRead.model_validate(deactivated)
