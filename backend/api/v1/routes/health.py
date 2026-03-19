"""
Health check endpoint for SCFCA backend.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Health check", tags=["health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
