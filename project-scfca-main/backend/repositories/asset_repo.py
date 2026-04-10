"""Asset repository — data access for Asset and FrozenValuation models.

FR-10: Asset registration.
FR-11: Frozen valuation snapshot creation.
FR-12: Asset facts immutability (enforced by ORM listeners).
FR-13: Metadata updates (status, notes) via approved tickets.
SR-15: Asset data immutability (enforced by ORM listeners).
"""

from __future__ import annotations

import random
import string
import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy.orm import Session

from backend.models.asset import Asset, FrozenValuation


def _generate_asset_id() -> str:
    suffix = "".join(random.choices(string.digits + "ABCDEF", k=4))
    return f"AS-{suffix}"


class AssetRepository:
    """Encapsulates all database operations for Asset entities."""

    def register(
        self,
        db: Session,
        *,
        case_id: str,
        symbol: str,
        asset_type: str,
        quantity: float,
        registered_by: uuid.UUID,
        protocol: str | None = None,
        network: str | None = None,
    ) -> Asset:
        """Register a new seized asset under a case. FR-10."""
        asset_id = _generate_asset_id()
        while db.query(Asset).filter(Asset.id == asset_id).first():
            asset_id = _generate_asset_id()

        asset = Asset(
            id=asset_id,
            case_id=case_id,
            symbol=symbol.upper(),
            asset_type=asset_type,
            quantity=quantity,
            protocol=protocol,
            network=network,
            status="registered",
            registered_by=registered_by,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    def get_by_id(self, db: Session, asset_id: str) -> Asset | None:
        return db.query(Asset).filter(Asset.id == asset_id.strip().upper()).first()

    def list_all(self, db: Session) -> Sequence[Asset]:
        return db.query(Asset).order_by(Asset.registered_at.desc()).all()

    def list_by_case(self, db: Session, case_id: str) -> Sequence[Asset]:
        return (
            db.query(Asset)
            .filter(Asset.case_id == case_id.strip().upper())
            .order_by(Asset.registered_at.desc())
            .all()
        )

    def update_metadata(
        self,
        db: Session,
        asset_id: str,
        *,
        status: str | None = None,
        notes: str | None = None,
    ) -> Asset:
        """Update mutable metadata fields only (FR-13). Immutable fields are protected by listeners."""
        asset = self.get_by_id(db, asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")
        if status is not None:
            asset.status = status
        if notes is not None:
            asset.notes = notes
        db.commit()
        db.refresh(asset)
        return asset

    def add_valuation(
        self,
        db: Session,
        *,
        asset_id: str,
        value: float,
        reference_currency: str = "USDT",
        source: str = "manual",
        snapshot_at: datetime | None = None,
    ) -> FrozenValuation:
        """Create a frozen valuation snapshot. FR-11 — INSERT-ONLY."""
        valuation = FrozenValuation(
            id=uuid.uuid4(),
            asset_id=asset_id,
            reference_currency=reference_currency.upper(),
            value=value,
            source=source,
            snapshot_at=snapshot_at or datetime.now(timezone.utc),
        )
        db.add(valuation)
        db.commit()
        db.refresh(valuation)
        return valuation

    def get_valuations(self, db: Session, asset_id: str) -> Sequence[FrozenValuation]:
        return (
            db.query(FrozenValuation)
            .filter(FrozenValuation.asset_id == asset_id)
            .order_by(FrozenValuation.snapshot_at.desc())
            .all()
        )


ASSET_REPO = AssetRepository()
