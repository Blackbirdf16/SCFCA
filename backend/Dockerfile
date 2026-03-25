# Backend Dockerfile for FastAPI app
# Builds a compact runtime image that runs: uvicorn backend.main:app
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps and runtime deps. Copy requirements if present for layer caching.
COPY backend/requirements.txt /app/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt || true \
    && apt-get remove -y build-essential gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY backend /app

EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
