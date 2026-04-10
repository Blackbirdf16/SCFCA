"""Audit endpoints for SCFCA backend.

SR-5: append-only audit log with hash chaining.
SR-12: security-relevant events are logged across sensitive operations.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.auth.dependencies import Principal, require_any_role
from backend.auth.schemas import Role
from backend.services.audit_log import AUDIT_LOG

router = APIRouter()


@router.get("/", summary="List audit events", tags=["audit"])
def list_audit_events(
    principal: Principal = Depends(require_any_role([Role.administrator, Role.auditor])),
):
    events = AUDIT_LOG.list(limit=200)
    return {
        "events": [
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "actorId": e.actor_id,
                "eventType": e.event_type,
                "action": e.action,
                "entityType": e.entity_type,
                "entityId": e.entity_id,
                "prevHash": e.prev_hash,
                "hash": e.hash,
                "details": e.details,
            }
            for e in events
        ]
    }


@router.get("/verify", summary="Verify audit hash chain", tags=["audit"])
def verify_audit_chain(
    principal: Principal = Depends(require_any_role([Role.administrator, Role.auditor])),
):
    return AUDIT_LOG.verify_chain()
