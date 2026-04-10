"""SQLAlchemy event listeners enforcing immutability constraints.

SR-15: Asset data immutability — quantity, symbol, asset_type cannot change.
SR-17: CaseIDs are never deleted.
FR-11: Frozen valuation snapshots are INSERT-ONLY.
FR-12: Asset facts (quantity, symbol, asset_type) are immutable once recorded.
"""

from __future__ import annotations

from sqlalchemy import event

from backend.models.asset import Asset, FrozenValuation
from backend.models.case import Case


# --- SR-15 / FR-12: Asset immutable fields ---

_ASSET_IMMUTABLE_FIELDS = {"quantity", "symbol", "asset_type"}


@event.listens_for(Asset, "before_update")
def _prevent_asset_fact_mutation(mapper, connection, target):
    """Raise if any immutable asset field is modified."""
    from sqlalchemy import inspect as sa_inspect

    state = sa_inspect(target)
    for field in _ASSET_IMMUTABLE_FIELDS:
        history = state.attrs[field].history
        if history.has_changes():
            raise ValueError(
                f"SR-15/FR-12 violation: cannot modify immutable asset field '{field}' "
                f"on asset {target.id}"
            )


@event.listens_for(Asset, "before_delete")
def _prevent_asset_delete(mapper, connection, target):
    """Assets cannot be deleted (SR-15)."""
    raise ValueError(f"SR-15 violation: cannot delete asset {target.id}")


# --- FR-11: Frozen valuation immutability ---

@event.listens_for(FrozenValuation, "before_update")
def _prevent_valuation_update(mapper, connection, target):
    """Frozen valuations are INSERT-ONLY (FR-11)."""
    raise ValueError(f"FR-11 violation: cannot update frozen valuation {target.id}")


@event.listens_for(FrozenValuation, "before_delete")
def _prevent_valuation_delete(mapper, connection, target):
    """Frozen valuations cannot be deleted (FR-11)."""
    raise ValueError(f"FR-11 violation: cannot delete frozen valuation {target.id}")


# --- SR-17: Case deletion prevention ---

@event.listens_for(Case, "before_delete")
def _prevent_case_delete(mapper, connection, target):
    """CaseIDs are never deleted (SR-17)."""
    raise ValueError(f"SR-17 violation: cannot delete case {target.id}")
