"""
SCFCA FastAPI application entry point.
"""
from fastapi import FastAPI
from backend.api.v1.routes import health, auth, cases

app = FastAPI(title="SCFCA - Secure Custody Framework for Cryptocurrency Assets")

# Include API routes
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["cases"])
