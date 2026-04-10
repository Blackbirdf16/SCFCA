"""Audit event ORM model for SCFCA.

SR-9:  Tamper-evident audit logs — append-only with hash chaining.
SR-10: Log deletion prevention — no DELETE/UPDATE operations exposed.
SR-11: Non-repudiation — every event tied to a pseudonymous actor_id.
"""

from sqlalchemy import Column, DateTime, Index, JSON, String, Text

from backend.core.database import Base


class AuditEventRecord(Base):
    """Persistent audit event with SHA-256 hash chain.

    This table is INSERT-ONLY. No UPDATE or DELETE operations are
    permitted at the application level (SR-10).

    Uses JSON (not JSONB) for cross-database compatibility in tests.
    PostgreSQL will still store this efficiently.
    """

    __tablename__ = "audit_events"

    id = Column(String(12), primary_key=True)  # AU-XXXXXX
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    actor_id = Column(String(24), nullable=False, index=True)
    event_type = Column(String(32), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    entity_type = Column(String(32), nullable=True)
    entity_id = Column(String(64), nullable=True)
    details = Column(JSON, nullable=True)
    prev_hash = Column(String(64), nullable=True)
    hash = Column(String(64), nullable=False, unique=True)

    __table_args__ = (
        Index("ix_audit_events_entity", "entity_type", "entity_id"),
    )
