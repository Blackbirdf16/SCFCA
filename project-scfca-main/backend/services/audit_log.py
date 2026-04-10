"""Append-only tamper-evident audit log with hash chaining.

SR-5: Audit integrity with hash chaining.
SR-12: Log security-relevant events.

PoC implementation uses in-memory storage with a clear repository boundary.
This is thesis-defensible and can be swapped for DB persistence later.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Iterable


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class AuditEvent:
    id: str
    timestamp: str
    actor_id: str
    event_type: str
    action: str
    entity_type: str | None
    entity_id: str | None
    details: dict[str, Any]
    prev_hash: str | None
    hash: str


class AuditLog:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: list[AuditEvent] = []

    def append(
        self,
        *,
        actor_id: str,
        event_type: str,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Append an audit event.

        No update/delete is supported (append-only).
        """
        if details is None:
            details = {}

        with self._lock:
            next_id = f"AU-{len(self._events) + 1:06d}"
            ts = _utc_now_iso()
            prev_hash = self._events[0].hash if self._events else None

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
            event = AuditEvent(
                id=next_id,
                timestamp=ts,
                actor_id=actor_id,
                event_type=event_type,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
                prev_hash=prev_hash,
                hash=digest,
            )

            # Prepend newest first (cheap list view for UI).
            self._events.insert(0, event)
            return event

    def list(self, *, limit: int = 200) -> list[AuditEvent]:
        with self._lock:
            return list(self._events[: max(1, min(limit, 2000))])

    def verify_chain(self) -> dict[str, Any]:
        """Verify hash chain integrity.

        Returns a report with status and the first failing event if any.
        """
        with self._lock:
            events = list(reversed(self._events))  # oldest -> newest

        prev_hash: str | None = None
        for ev in events:
            payload = {
                "id": ev.id,
                "timestamp": ev.timestamp,
                "actor_id": ev.actor_id,
                "event_type": ev.event_type,
                "action": ev.action,
                "entity_type": ev.entity_type,
                "entity_id": ev.entity_id,
                "details": ev.details,
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


# Singleton audit log for the PoC runtime.
AUDIT_LOG = AuditLog()
