"""
Audit logging service for SCFCA PoC.
Provides helper functions to log audit events, including optional hash chaining.
"""
from backend.core.models import AuditEvent, User
from backend.core.database import SessionLocal
from sqlalchemy import desc
from hashlib import sha256
from typing import Optional

def get_last_event(db) -> Optional[AuditEvent]:
    return db.query(AuditEvent).order_by(desc(AuditEvent.id)).first()

def compute_hash(event: AuditEvent, previous_hash: Optional[str]) -> str:
    data = f"{event.actor_id}|{event.action}|{event.timestamp}|{event.entity_type}|{event.entity_id}|{event.details}|{previous_hash or ''}"
    return sha256(data.encode()).hexdigest()

def log_audit(actor: User, action: str, entity_type: str, entity_id: int, details: str):
    db = SessionLocal()
    # Prepare event (timestamp is auto-set by DB)
    event = AuditEvent(
        actor_id=actor.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    # Hash chain (optional, for PoC integrity)
    last_event = get_last_event(db)
    previous_hash = last_event.hash_chain if last_event else None
    event.hash_chain = compute_hash(event, previous_hash)
    db.add(event)
    db.commit()
    db.close()

def list_audit_events(limit: int = 100):
    db = SessionLocal()
    events = db.query(AuditEvent).order_by(desc(AuditEvent.timestamp)).limit(limit).all()
    db.close()
    return events
