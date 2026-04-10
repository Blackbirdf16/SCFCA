"""Asset ORM models for SCFCA.

FR-10: Asset registration under a CaseID with type, quantity, metadata.
FR-11: Frozen reference valuation snapshot — immutable after creation.
FR-12: Asset facts (type, quantity) are immutable once recorded.
SR-15: Original seized asset records cannot be modified.
NFR-13: Reference currency is configurable.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.models.user import UUIDType


class Asset(Base):
    """A seized cryptocurrency asset registered under a case.

    quantity, symbol, and asset_type are immutable after creation (FR-12, SR-15).
    Only metadata fields (status, notes) may be updated via approved tickets (FR-13).
    """

    __tablename__ = "assets"

    id = Column(String(8), primary_key=True)  # AS-XXXX
    case_id = Column(String(8), ForeignKey("cases.id"), nullable=False, index=True)
    symbol = Column(String(16), nullable=False)  # BTC, ETH, SOL, USDC...
    asset_type = Column(String(32), nullable=False)  # native, token, nft
    quantity = Column(Numeric(28, 8), nullable=False)  # FR-12: immutable
    protocol = Column(String(32), nullable=True)
    network = Column(String(32), nullable=True)
    status = Column(String(32), nullable=False, default="registered")  # mutable via ticket
    notes = Column(String(512), nullable=True)  # mutable via ticket
    registered_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    registered_by = Column(UUIDType(), ForeignKey("users.id"), nullable=False)

    # Relationships
    case = relationship("Case")
    valuations = relationship("FrozenValuation", back_populates="asset", order_by="FrozenValuation.snapshot_at.desc()")


class FrozenValuation(Base):
    """Frozen reference valuation snapshot at the time of seizure.

    FR-11: Immutable — INSERT-ONLY, no UPDATE or DELETE.
    NFR-13: reference_currency is configurable (default USDT).
    """

    __tablename__ = "frozen_valuations"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String(8), ForeignKey("assets.id"), nullable=False, index=True)
    reference_currency = Column(String(8), nullable=False, default="USDT")
    value = Column(Numeric(28, 8), nullable=False)
    source = Column(String(128), nullable=False)  # "manual", "coingecko", etc.
    snapshot_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    asset = relationship("Asset", back_populates="valuations")
