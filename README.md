# SCFCA: Secure Custody Framework for Cryptocurrency Assets

## Setup & Run (Local Demo)

### 1. Clone the repository
```
git clone <repo-url>
cd scfca-repo
```

### 2. Set up backend (FastAPI)
- Install Python 3.10+
- Install dependencies:
	```
	cd backend
	pip install -r requirements.txt
	```
- Seed demo data:
	```
	cd ../scripts
	python seed_demo_data.py
	```
- Run backend API:
	```
	cd ../backend
	uvicorn main:app --reload
	```
	API docs: http://localhost:8000/docs

### 3. (Optional) Run tests
```
cd ../tests
pytest
```

### 4. Frontend (Streamlit)
- (If implemented) Run Streamlit UI:
	```
	cd ../frontend
	streamlit run app.py
	```

---

## Demo Walkthrough

### Case Handler
- Login as: `alice` / `alice123`
- View assigned cases
- Upload/view documents
- Cannot access user management or audit logs

### Administrator
- Login as: `bob` / `bob123` or `eve` / `eve123`
- View all users
- Approve/reject tickets (dual approval)
- Manage cases/assets
- Full access except audit-only views

### Auditor
- Login as: `carol` / `carol123`
- View audit logs and traceability
- Cannot modify cases/assets/tickets
- Read-only access for compliance

---

## Key Workflows (Tested)
- Login (all roles)
- Case listing (case handler)
- User listing (admin only)
- Audit log access (auditor only)
- Ticket approval (admin)
- RBAC enforced (e.g., case handler cannot see users)

---

## Notes
- This PoC is for academic demonstration only.
- All credentials and data are for demo use.
- For thesis, see `docs/` and `diagrams/` for architecture and rationale.
