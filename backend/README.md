# Backend

FastAPI backend for the SCFCA proof of concept.

## Run locally

From the repository root:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health

API and business logic for SCFCA. Organized by domain:
- auth
- users
- roles
- cases
- tickets
- assets
- custody
- audit
- documents
- common
- config
- middleware
- validators
- models
- services
- repositories
- tests

Each folder contains placeholder files for future implementation.