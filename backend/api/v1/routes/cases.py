"""
Case management endpoints for SCFCA backend (placeholder).
"""
from fastapi import APIRouter, Depends

from backend.auth.dependencies import Principal, get_current_principal
from backend.auth.schemas import Role

router = APIRouter()


DEMO_CASES = [
    {
        "id": "C-100",
        "walletRef": "WLT-8F3A-PRIMARY",
        "title": "Corporate cold wallet rotation",
        "handler": "ops_team",
        "custodyStatus": "open",
        "holdings": [
            {"symbol": "BTC", "balance": 12.5},
            {"symbol": "ETH", "balance": 180},
        ],
    },
    {
        "id": "C-101",
        "walletRef": "WLT-21C9-MSIG",
        "title": "Multi-sig governance update",
        "handler": "admin_team",
        "custodyStatus": "in_review",
        "holdings": [
            {"symbol": "BTC", "balance": 2},
            {"symbol": "USDC", "balance": 500000},
        ],
    },
]

@router.get("/", summary="List cases", tags=["cases"])
def list_cases(principal: Principal = Depends(get_current_principal)):
    """List wallet-linked custody cases (PoC placeholder).

    A case represents an institutional custody record linked to a real wallet
    reference. This endpoint intentionally returns static demo data and does
    not implement any blockchain connectivity.
    """
    cases = DEMO_CASES
    if principal.role == Role.regular:
        cases = [c for c in DEMO_CASES if c.get("handler") == principal.username]
    return {"cases": cases}
