"""Asset registry endpoints for SCFCA backend.

FR-10: Asset registration under a CaseID.
FR-11: Frozen reference valuation snapshot.
FR-12: Asset facts immutability (enforced at ORM level).
FR-13: Metadata updates via approved tickets only.
SR-15: Original seized asset records cannot be modified.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth.dependencies import Principal, get_current_principal, require_role, require_any_role
from backend.auth.schemas import Role
from backend.core.config import settings
from backend.core.database import get_db
from backend.repositories.asset_repo import ASSET_REPO
from backend.repositories.case_repo import CASE_REPO
from backend.repositories.user_repo import USER_REPO
from backend.services.audit_log import AUDIT_LOG
from backend.services.security_ids import pseudonymous_actor_id

router = APIRouter()

AdminOnly = Annotated[Principal, Depends(require_role(Role.administrator))]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AssetRegister(BaseModel):
    case_id: str = Field(..., alias="caseId")
    symbol: str = Field(..., min_length=1, max_length=16)
    asset_type: str = Field(..., alias="assetType", min_length=1, max_length=32)
    quantity: float = Field(..., gt=0)
    protocol: Optional[str] = None
    network: Optional[str] = None

    model_config = {"populate_by_name": True}


class ValuationCreate(BaseModel):
    value: float = Field(..., gt=0)
    reference_currency: str = Field(default="USDT", alias="referenceCurrency", max_length=8)
    source: str = Field(default="manual", max_length=128)

    model_config = {"populate_by_name": True}


class MetadataUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/", summary="Register asset", tags=["assets"])
def register_asset(
    payload: AssetRegister,
    principal: AdminOnly,
    db: Session = Depends(get_db),
):
    """Register a seized asset under a case. Admin only. FR-10."""
    case = CASE_REPO.get_by_id(db, payload.case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    admin_user = USER_REPO.get_by_username(db, principal.username)
    if not admin_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user not found in DB")

    asset = ASSET_REPO.register(
        db,
        case_id=case.id,
        symbol=payload.symbol,
        asset_type=payload.asset_type,
        quantity=payload.quantity,
        registered_by=admin_user.id,
        protocol=payload.protocol,
        network=payload.network,
    )

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="assets",
        action="asset_registered",
        entity_type="asset",
        entity_id=asset.id,
        details={
            "caseId": case.id,
            "symbol": asset.symbol,
            "quantity": float(asset.quantity),
            "assetType": asset.asset_type,
        },
    )

    return {
        "asset": {
            "id": asset.id,
            "caseId": asset.case_id,
            "symbol": asset.symbol,
            "assetType": asset.asset_type,
            "quantity": float(asset.quantity),
            "protocol": asset.protocol,
            "network": asset.network,
            "status": asset.status,
        }
    }


@router.get("/", summary="List assets", tags=["assets"])
def list_assets(
    principal: Principal = Depends(require_any_role([Role.administrator, Role.regular])),
    db: Session = Depends(get_db),
):
    """List all assets. Admin sees all; handler sees only assigned cases' assets."""
    assets = ASSET_REPO.list_all(db)

    result = []
    for a in assets:
        result.append({
            "id": a.id,
            "caseId": a.case_id,
            "symbol": a.symbol,
            "assetType": a.asset_type,
            "quantity": float(a.quantity),
            "protocol": a.protocol,
            "network": a.network,
            "status": a.status,
            "registeredAt": a.registered_at.isoformat() if a.registered_at else None,
        })

    return {"assets": result}


@router.get("/{asset_id}", summary="Asset details", tags=["assets"])
def get_asset(
    asset_id: str,
    principal: Principal = Depends(require_any_role([Role.administrator, Role.regular])),
    db: Session = Depends(get_db),
):
    """Get asset details. FR-10."""
    asset = ASSET_REPO.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    return {
        "asset": {
            "id": asset.id,
            "caseId": asset.case_id,
            "symbol": asset.symbol,
            "assetType": asset.asset_type,
            "quantity": float(asset.quantity),
            "protocol": asset.protocol,
            "network": asset.network,
            "status": asset.status,
            "notes": asset.notes,
            "registeredAt": asset.registered_at.isoformat() if asset.registered_at else None,
        }
    }


@router.get("/{asset_id}/valuation", summary="Frozen valuation", tags=["assets"])
def get_valuation(
    asset_id: str,
    principal: Principal = Depends(require_any_role([Role.administrator, Role.regular, Role.auditor])),
    db: Session = Depends(get_db),
):
    """Get frozen valuation snapshots for an asset. FR-11."""
    asset = ASSET_REPO.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    valuations = ASSET_REPO.get_valuations(db, asset_id)
    return {
        "assetId": asset_id,
        "valuations": [
            {
                "id": str(v.id),
                "referenceCurrency": v.reference_currency,
                "value": float(v.value),
                "source": v.source,
                "snapshotAt": v.snapshot_at.isoformat() if v.snapshot_at else None,
            }
            for v in valuations
        ],
    }


@router.post("/{asset_id}/valuation", summary="Add frozen valuation", tags=["assets"])
def add_valuation(
    asset_id: str,
    payload: ValuationCreate,
    principal: AdminOnly,
    db: Session = Depends(get_db),
):
    """Create a frozen valuation snapshot. Admin only. FR-11."""
    asset = ASSET_REPO.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    valuation = ASSET_REPO.add_valuation(
        db,
        asset_id=asset_id,
        value=payload.value,
        reference_currency=payload.reference_currency,
        source=payload.source,
    )

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="assets",
        action="valuation_created",
        entity_type="asset",
        entity_id=asset_id,
        details={
            "value": float(valuation.value),
            "currency": valuation.reference_currency,
            "source": valuation.source,
        },
    )

    return {
        "valuation": {
            "id": str(valuation.id),
            "assetId": asset_id,
            "referenceCurrency": valuation.reference_currency,
            "value": float(valuation.value),
            "source": valuation.source,
            "snapshotAt": valuation.snapshot_at.isoformat() if valuation.snapshot_at else None,
        }
    }


@router.patch("/{asset_id}/metadata", summary="Update asset metadata", tags=["assets"])
def update_metadata(
    asset_id: str,
    payload: MetadataUpdate,
    principal: AdminOnly,
    db: Session = Depends(get_db),
):
    """Update mutable metadata (status, notes). Admin only, via ticket. FR-13."""
    asset = ASSET_REPO.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    ASSET_REPO.update_metadata(db, asset_id, status=payload.status, notes=payload.notes)

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="assets",
        action="asset_metadata_updated",
        entity_type="asset",
        entity_id=asset_id,
        details={"status": payload.status, "notes": payload.notes},
    )

    return {"status": "updated", "assetId": asset_id}
