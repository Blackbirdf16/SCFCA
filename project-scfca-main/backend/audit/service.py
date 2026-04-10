"""Audit logging service (append-only, hash-chained).

This module exists for backward compatibility with earlier PoC scaffolding.
It intentionally avoids database dependencies so the repo stays runnable
without provisioning a DB service.
"""

from __future__ import annotations

from typing import Any

from backend.services.audit_log import AUDIT_LOG, AuditEvent


def log_event(
    *,
    actor_id: str,
    event_type: str,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditEvent:
    return AUDIT_LOG.append(
        actor_id=actor_id,
        event_type=event_type,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )


def list_events(*, limit: int = 100) -> list[AuditEvent]:
    return AUDIT_LOG.list(limit=limit)


def verify_chain() -> dict[str, Any]:
    return AUDIT_LOG.verify_chain()
