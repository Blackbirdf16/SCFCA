"""SQLAlchemy ORM models for SCFCA.

All models import Base from core.database and are registered
via this package so Alembic can auto-detect them.
"""

from backend.models.user import User  # noqa: F401
from backend.models.audit_event import AuditEventRecord  # noqa: F401
from backend.models.case import Case, CaseAssignmentHistory  # noqa: F401
from backend.models.asset import Asset, FrozenValuation  # noqa: F401
from backend.models.ticket import Ticket, TicketApproval, TicketExecution  # noqa: F401
from backend.models.document import DocumentRecord  # noqa: F401
from backend.models.mfa import UserMFA  # noqa: F401

import backend.models.listeners  # noqa: F401 — activates event listeners

__all__ = [
    "User",
    "AuditEventRecord",
    "Case",
    "CaseAssignmentHistory",
    "Asset",
    "FrozenValuation",
    "Ticket",
    "TicketApproval",
    "TicketExecution",
    "DocumentRecord",
    "UserMFA",
]
