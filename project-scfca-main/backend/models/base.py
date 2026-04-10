"""Shared model mixins for SCFCA ORM models.

Provides reusable columns (timestamps) to avoid repetition across models.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime


class TimestampMixin:
    """Adds created_at and updated_at columns to any model."""

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )
