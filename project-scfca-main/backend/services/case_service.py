"""Case domain service with confidentiality controls and DB support.

FR-5:  Case creation (admin only).
FR-6:  Case assignment — one handler at a time.
FR-7:  Case index visibility for all authenticated users.
FR-8:  Case reassignment via approved ticket.
FR-9:  Assignment history tracking.
FR-17: Case visibility and confidentiality — role/assignment gated.

Dual-mode: uses database if available, falls back to in-memory demo data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.auth.dependencies import Principal
from backend.auth.schemas import Role


# ---------------------------------------------------------------------------
# In-memory demo data (fallback for tests without DB)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CaseDTO:
    id: str
    wallet_ref: str
    title: str
    handler: str
    custody_status: str
    holdings: list[dict[str, Any]]


_DEMO_CASES: dict[str, CaseDTO] = {
    "C-100": CaseDTO(
        id="C-100",
        wallet_ref="WLT-8F3A-PRIMARY",
        title="Corporate cold wallet rotation",
        handler="alice",
        custody_status="open",
        holdings=[{"symbol": "BTC", "balance": 12.5}, {"symbol": "ETH", "balance": 180}],
    ),
    "C-101": CaseDTO(
        id="C-101",
        wallet_ref="WLT-21C9-MSIG",
        title="Multi-sig governance update",
        handler="alice",
        custody_status="in_review",
        holdings=[{"symbol": "BTC", "balance": 2}, {"symbol": "USDC", "balance": 500000}],
    ),
}


# ---------------------------------------------------------------------------
# Public API (used by case routes, ticket routes, document routes)
# ---------------------------------------------------------------------------

def list_case_index() -> list[dict[str, Any]]:
    """Return minimal case index. FR-7."""
    return [{"id": c.id, "custodyStatus": c.custody_status} for c in _DEMO_CASES.values()]


def get_case(case_id: str) -> CaseDTO | None:
    key = (case_id or "").strip().upper()
    return _DEMO_CASES.get(key)


def is_case_assigned_to(principal: Principal, case_id: str, db=None) -> bool:
    """Check if a case is assigned to the given principal. FR-6.

    If a DB session is provided, checks DB first; falls back to in-memory demo data.
    """
    if db is not None:
        try:
            from backend.repositories.case_repo import CASE_REPO
            case_model = CASE_REPO.get_by_id(db, case_id)
            if case_model is not None:
                if hasattr(case_model, "handler") and case_model.handler:
                    return case_model.handler.username == principal.username
                return False
        except Exception:
            pass

    # Fallback to in-memory
    c = get_case(case_id)
    return bool(c and c.handler == principal.username)


def case_detail_for(principal: Principal, case: CaseDTO) -> dict[str, Any]:
    """Return role-appropriate case detail. FR-17."""
    # Auditors: data minimization / redaction.
    if principal.role == Role.auditor:
        return {
            "id": case.id,
            "custodyStatus": case.custody_status,
            "holdings": [{"symbol": h.get("symbol")} for h in case.holdings],
            "redacted": True,
        }

    # Regular case handlers can only view assigned cases.
    if principal.role == Role.regular and case.handler != principal.username:
        raise PermissionError("case_not_assigned")

    return {
        "id": case.id,
        "walletRef": case.wallet_ref,
        "title": case.title,
        "handler": case.handler,
        "custodyStatus": case.custody_status,
        "holdings": case.holdings,
        "redacted": False,
    }


# ---------------------------------------------------------------------------
# DB-aware helpers (used by expanded case routes in Phase 2+)
# ---------------------------------------------------------------------------

def case_model_to_detail(case_model, principal: Principal, assets=None) -> dict[str, Any]:
    """Convert a Case ORM model to a role-appropriate detail dict."""
    holdings = []
    if assets:
        holdings = [
            {"symbol": a.symbol, "balance": float(a.quantity)}
            for a in assets
        ]

    handler_name = ""
    if hasattr(case_model, "handler") and case_model.handler:
        handler_name = case_model.handler.username

    if principal.role == Role.auditor:
        return {
            "id": case_model.id,
            "custodyStatus": case_model.custody_status,
            "holdings": [{"symbol": h["symbol"]} for h in holdings],
            "redacted": True,
        }

    if principal.role == Role.regular and handler_name != principal.username:
        raise PermissionError("case_not_assigned")

    return {
        "id": case_model.id,
        "walletRef": case_model.wallet_ref,
        "title": case_model.title,
        "handler": handler_name,
        "custodyStatus": case_model.custody_status,
        "holdings": holdings,
        "redacted": False,
    }
