"""Case management endpoints for SCFCA backend.

FR-5:  Case creation (admin only).
FR-6:  Case assignment — one handler at a time.
FR-7:  Case index visibility for all authenticated users.
FR-8:  Case reassignment via approved ticket.
FR-9:  Assignment history.
FR-17: Case visibility and confidentiality.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth.dependencies import Principal, get_current_principal, require_role, require_any_role
from backend.auth.schemas import Role
from backend.core.config import settings
from backend.core.database import get_db
from backend.repositories.case_repo import CASE_REPO
from backend.repositories.asset_repo import ASSET_REPO
from backend.repositories.audit_repo import AUDIT_REPO
from backend.repositories.user_repo import USER_REPO
from backend.services.audit_log import AUDIT_LOG
from backend.services.case_service import (
    case_detail_for,
    case_model_to_detail,
    get_case,
    list_case_index,
)
from backend.services.security_ids import pseudonymous_actor_id

router = APIRouter()

AdminOnly = Annotated[Principal, Depends(require_role(Role.administrator))]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=256)
    wallet_ref: str = Field(..., min_length=3, max_length=64)
    handler_username: str = Field(..., min_length=2, max_length=64)


class ReassignRequest(BaseModel):
    new_handler_username: str = Field(..., min_length=2, max_length=64)
    ticket_id: str | None = None


# ---------------------------------------------------------------------------
# Existing endpoints (in-memory fallback for backward compat with tests)
# ---------------------------------------------------------------------------

@router.get("/", summary="List cases", tags=["cases"])
def list_cases(
    principal: Principal = Depends(get_current_principal),
    db: Session | None = Depends(get_db),
):
    """List case index (IDs + status). All authenticated users. FR-7."""
    # Try DB first
    if db is not None:
        try:
            index = CASE_REPO.list_index(db)
            if index:
                return {"cases": index}
        except Exception:
            pass

    # Fallback to in-memory demo data
    return {"cases": list_case_index()}


@router.get("/{case_id}", summary="Get case details", tags=["cases"])
def get_case_details(
    case_id: str,
    principal: Principal = Depends(get_current_principal),
    db: Session | None = Depends(get_db),
):
    """Get case details with role-based visibility. FR-6, FR-17."""
    # Try DB first
    if db is not None:
        try:
            case_model = CASE_REPO.get_by_id(db, case_id)
            if case_model is not None:
                assets = ASSET_REPO.list_by_case(db, case_id)
                try:
                    detail = case_model_to_detail(case_model, principal, assets)
                    return {"case": detail}
                except PermissionError:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        except HTTPException:
            raise
        except Exception:
            pass

    # Fallback to in-memory
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    try:
        return {"case": case_detail_for(principal, case)}
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


# ---------------------------------------------------------------------------
# New DB-backed endpoints (Phase 2)
# ---------------------------------------------------------------------------

@router.post("/", summary="Create case", tags=["cases"])
def create_case(
    payload: CaseCreate,
    principal: AdminOnly,
    db: Session = Depends(get_db),
):
    """Create a new custody case. Admin only. FR-5."""
    handler = USER_REPO.get_by_username(db, payload.handler_username)
    if not handler or not handler.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Handler user not found or inactive")

    # Look up admin's UUID for created_by
    admin_user = USER_REPO.get_by_username(db, principal.username)
    admin_id = admin_user.id if admin_user else handler.id

    case = CASE_REPO.create(
        db,
        title=payload.title,
        wallet_ref=payload.wallet_ref,
        handler_id=handler.id,
        created_by=admin_id,
    )

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="cases",
        action="case_created",
        entity_type="case",
        entity_id=case.id,
        details={"title": case.title, "handler": payload.handler_username},
    )

    return {
        "case": {
            "id": case.id,
            "title": case.title,
            "walletRef": case.wallet_ref,
            "handler": payload.handler_username,
            "custodyStatus": case.custody_status,
        }
    }


@router.patch("/{case_id}/reassign", summary="Reassign case handler", tags=["cases"])
def reassign_case(
    case_id: str,
    payload: ReassignRequest,
    principal: AdminOnly,
    db: Session = Depends(get_db),
):
    """Reassign case handler. Admin only. FR-8, FR-9."""
    case = CASE_REPO.get_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    new_handler = USER_REPO.get_by_username(db, payload.new_handler_username)
    if not new_handler or not new_handler.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New handler not found or inactive")

    admin_user = USER_REPO.get_by_username(db, principal.username)
    admin_id = admin_user.id if admin_user else new_handler.id

    old_handler_name = case.handler.username if case.handler else "unknown"

    CASE_REPO.reassign(
        db,
        case_id=case_id,
        new_handler_id=new_handler.id,
        assigned_by=admin_id,
        ticket_id=payload.ticket_id,
    )

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="cases",
        action="case_reassigned",
        entity_type="case",
        entity_id=case_id,
        details={
            "from": old_handler_name,
            "to": payload.new_handler_username,
            "ticket_id": payload.ticket_id,
        },
    )

    return {"status": "reassigned", "caseId": case_id, "newHandler": payload.new_handler_username}


@router.get("/{case_id}/history", summary="Assignment history", tags=["cases"])
def get_assignment_history(
    case_id: str,
    principal: Principal = Depends(require_any_role([Role.administrator, Role.auditor])),
    db: Session = Depends(get_db),
):
    """Get case assignment history. Admin/auditor only. FR-9."""
    history = CASE_REPO.get_assignment_history(db, case_id)
    return {
        "history": [
            {
                "caseId": h.case_id,
                "fromUser": str(h.from_user_id) if h.from_user_id else None,
                "toUser": str(h.to_user_id),
                "ticketId": h.ticket_id,
                "assignedBy": str(h.assigned_by),
                "assignedAt": h.assigned_at.isoformat() if h.assigned_at else None,
            }
            for h in history
        ]
    }
