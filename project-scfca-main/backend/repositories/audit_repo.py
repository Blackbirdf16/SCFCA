"""Audit event repository — data access for AuditEventRecord model.

SR-9:  Tamper-evident audit logs with hash chaining.
SR-10: Log deletion prevention — only INSERT is exposed.
SR-11: Non-repudiation — every event has an actor_id.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Sequence

from sqlalchemy.orm import Session

from backend.models.audit_event import AuditEventRecord


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class AuditRepository:
    """Append-only repository for audit events with hash chaining.

    This repository only exposes INSERT and SELECT operations.
    No UPDATE or DELETE is available (SR-10).
    """

    def _next_id(self, db: Session) -> str:
        count = db.query(AuditEventRecord).count()
        return f"AU-{count + 1:06d}"

    def _get_last_hash(self, db: Session) -> str | None:
        last = (
            db.query(AuditEventRecord)
            .order_by(AuditEventRecord.id.desc())
            .first()
        )
        return last.hash if last else None

    def append(
        self,
        db: Session,
        *,
        actor_id: str,
        event_type: str,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEventRecord:
        """Append a new audit event with hash chaining."""
        if details is None:
            details = {}

        next_id = self._next_id(db)
        ts = _utc_now_iso()
        prev_hash = self._get_last_hash(db)

        payload = {
            "id": next_id,
            "timestamp": ts,
            "actor_id": actor_id,
            "event_type": event_type,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "prev_hash": prev_hash,
        }
        digest = sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

        record = AuditEventRecord(
            id=next_id,
            timestamp=datetime.fromisoformat(ts),
            actor_id=actor_id,
            event_type=event_type,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            prev_hash=prev_hash,
            hash=digest,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list(self, db: Session, *, limit: int = 200) -> Sequence[AuditEventRecord]:
        """Return newest events first."""
        return (
            db.query(AuditEventRecord)
            .order_by(AuditEventRecord.id.desc())
            .limit(min(limit, 2000))
            .all()
        )

    def verify_chain(self, db: Session) -> dict[str, Any]:
        """Verify hash chain integrity from oldest to newest."""
        events = (
            db.query(AuditEventRecord)
            .order_by(AuditEventRecord.id.asc())
            .all()
        )

        prev_hash: str | None = None
        for ev in events:
            payload = {
                "id": ev.id,
                "timestamp": ev.timestamp.isoformat(timespec="seconds") if isinstance(ev.timestamp, datetime) else ev.timestamp,
                "actor_id": ev.actor_id,
                "event_type": ev.event_type,
                "action": ev.action,
                "entity_type": ev.entity_type,
                "entity_id": ev.entity_id,
                "details": ev.details or {},
                "prev_hash": prev_hash,
            }
            expected = sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
            if ev.prev_hash != prev_hash or ev.hash != expected:
                return {
                    "ok": False,
                    "failedEventId": ev.id,
                    "reason": "hash_mismatch",
                }
            prev_hash = ev.hash

        return {"ok": True, "count": len(events)}


# Module-level singleton for convenience.
AUDIT_REPO = AuditRepository()
