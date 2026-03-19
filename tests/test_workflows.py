"""
Basic tests for SCFCA PoC key workflows.
Run with: pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Demo credentials (seeded by scripts/seed_demo_data.py)
USERS = {
    "case_handler": {"username": "alice", "password": "alice123"},
    "administrator": {"username": "bob", "password": "bob123"},
    "auditor": {"username": "carol", "password": "carol123"},
}

def login(role):
    resp = client.post("/api/v1/auth/login", json=USERS[role])
    assert resp.status_code == 200
    return resp.cookies

def test_case_handler_dashboard():
    cookies = login("case_handler")
    resp = client.get("/api/v1/dashboard/summary", cookies=cookies)
    assert resp.status_code == 200
    data = resp.json()
    assert "case_count" in data

def test_admin_can_see_users():
    cookies = login("administrator")
    resp = client.get("/api/v1/users/", cookies=cookies)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_auditor_can_see_audit_log():
    cookies = login("auditor")
    resp = client.get("/api/v1/audit/", cookies=cookies)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_case_handler_cannot_see_users():
    cookies = login("case_handler")
    resp = client.get("/api/v1/users/", cookies=cookies)
    assert resp.status_code == 403

def test_admin_can_approve_ticket():
    cookies = login("administrator")
    # Get a pending ticket
    resp = client.get("/api/v1/tickets/", cookies=cookies)
    assert resp.status_code == 200
    tickets = resp.json()
    pending = [t for t in tickets if t["status"] == "pending"]
    if not pending:
        pytest.skip("No pending tickets to approve")
    ticket_id = pending[0]["id"]
    # Approve
    resp = client.post(f"/api/v1/tickets/{ticket_id}/approve", cookies=cookies)
    assert resp.status_code in (200, 400)  # 400 if already approved
