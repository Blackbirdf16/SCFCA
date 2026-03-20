"""Audit endpoints for SCFCA backend (PoC).

Role intent:
- regular: no access to system-wide logs
- administrator: operational log review
- auditor: evidence/traceability focused review

Demo-safe only: in-memory events; no sensitive fields.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.auth.dependencies import Principal, require_any_role
from backend.auth.schemas import Role

router = APIRouter()


class AuditEventRecord(BaseModel):
    id: str
    timestamp: str
    actor: str
    action: str


AUDIT_EVENTS: list[AuditEventRecord] = [
    AuditEventRecord(id="AU-001", timestamp="2026-03-19 10:05", actor="auditor01", action="Checked signature chain"),
    AuditEventRecord(id="AU-002", timestamp="2026-03-19 10:25", actor="admin01", action="Updated ticket policy"),
    AuditEventRecord(id="AU-003", timestamp="2026-03-19 11:20", actor="ops_team", action="Opened transfer request (PoC)"),
]


@router.get("/", summary="List audit events", tags=["audit"])
def list_audit_events(
    principal: Principal = Depends(require_any_role([Role.administrator, Role.auditor])),
):
    return {"events": [e.model_dump() for e in AUDIT_EVENTS]}
