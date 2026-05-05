"""Basic tests for active SCFCA PoC workflows."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def login(username: str, password: str, role: str):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password, "role": role},
    )
    assert response.status_code == 200
    csrf_token = response.cookies.get("scfca_csrf")
    assert csrf_token
    return response.cookies, {"x-csrf-token": csrf_token}


def test_regular_user_can_see_assigned_cases():
    cookies, _headers = login("alice", "alice123", "regular")

    response = client.get("/api/v1/cases/", cookies=cookies)

    assert response.status_code == 200
    assert "cases" in response.json()


def test_admin_can_see_tickets():
    cookies, _headers = login("bob", "bob123", "administrator")

    response = client.get("/api/v1/tickets/", cookies=cookies)

    assert response.status_code == 200
    assert "tickets" in response.json()


def test_auditor_can_see_audit_log():
    cookies, _headers = login("carol", "carol123", "auditor")

    response = client.get("/api/v1/audit/", cookies=cookies)

    assert response.status_code == 200
    assert "events" in response.json()


def test_regular_user_cannot_see_audit_log():
    cookies, _headers = login("alice", "alice123", "regular")

    response = client.get("/api/v1/audit/", cookies=cookies)

    assert response.status_code == 403


def test_admin_can_create_ticket_with_csrf():
    cookies, headers = login("bob", "bob123", "administrator")

    response = client.post(
        "/api/v1/tickets/",
        cookies=cookies,
        headers=headers,
        json={
            "caseId": "C-100",
            "ticketType": "transfer_request",
            "description": "Workflow test transfer request",
            "linkedDocumentIds": [],
        },
    )

    assert response.status_code == 200
    assert response.json()["ticket"]["status"] == "pending_review"
