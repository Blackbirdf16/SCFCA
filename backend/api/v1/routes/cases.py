"""
Case management endpoints for SCFCA backend (placeholder).
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="List cases", tags=["cases"])
def list_cases():
    """Placeholder for listing cases."""
    return {"cases": []}
