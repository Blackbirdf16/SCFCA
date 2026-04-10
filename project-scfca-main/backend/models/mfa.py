"""MFA ORM model for SCFCA.

SR-5: MFA (TOTP) for privileged roles.
Administrators must enroll and use TOTP for login after setup.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func

from backend.core.database import Base
from backend.models.user import UUIDType


class UserMFA(Base):
    """TOTP enrollment record for a user.

    When is_enabled=True, the user's login flow requires a TOTP challenge
    after password verification.
    """

    __tablename__ = "user_mfa"

    user_id = Column(UUIDType(), ForeignKey("users.id"), primary_key=True)
    totp_secret = Column(String(64), nullable=False)
    is_enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
