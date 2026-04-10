"""Pytest suite for SCFCA hardened PoC workflows.

Focus: security-first backend controls that must be enforced server-side.
Run with: pytest tests/
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.main import app


USERS = {
    "alice": {"username": "alice", "password": "alice123"},
    "bob": {"username": "bob", "password": "bob123"},
    "eve": {"username": "eve", "password": "eve123"},
    "carol": {"username": "carol", "password": "carol123"},
}


def login(client: TestClient, username: str) -> tuple[dict[str, str], str]:
    resp = client.post("/api/v1/auth/login", json=USERS[username])
    assert resp.status_code == 200
    csrf = resp.cookies.get(settings.csrf_cookie_name)
    assert csrf
    return resp.cookies, csrf


def test_login_sets_cookie_and_me_works():
    client = TestClient(app)
    cookies, _csrf = login(client, "alice")
    resp = client.get("/api/v1/auth/me", cookies=cookies)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "alice"
    assert data["role"] == "regular"


def test_csrf_blocks_unsafe_without_header():
    client = TestClient(app)
    cookies, _csrf = login(client, "alice")

    # POST should fail without X-CSRF-Token header.
    resp = client.post(
        "/api/v1/tickets/",
        json={"caseId": "C-100", "ticketType": "transfer_request", "description": "test"},
        cookies=cookies,
    )
    assert resp.status_code == 403


def test_ticket_dual_approval_execution_idempotency_and_replay_protection():
    client = TestClient(app)

    alice_cookies, alice_csrf = login(client, "alice")
    create = client.post(
        "/api/v1/tickets/",
        json={"caseId": "C-100", "ticketType": "transfer_request", "description": "PoC execution test"},
        cookies=alice_cookies,
        headers={"x-csrf-token": alice_csrf},
    )
    assert create.status_code == 200
    ticket_id = create.json()["ticket"]["id"]

    bob_cookies, bob_csrf = login(client, "bob")
    approve1 = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf},
    )
    assert approve1.status_code == 200
    assert approve1.json()["ticket"]["status"] == "awaiting_second_approval"

    eve_cookies, eve_csrf = login(client, "eve")
    approve2 = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        cookies=eve_cookies,
        headers={"x-csrf-token": eve_csrf},
    )
    assert approve2.status_code == 200
    assert approve2.json()["ticket"]["status"] == "approved"

    assign = client.patch(
        f"/api/v1/tickets/{ticket_id}/assign",
        json={"assignedTo": "bob"},
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf},
    )
    assert assign.status_code == 200
    assert assign.json()["ticket"]["assignedTo"] == "bob"

    # SR-6: Obtain re-auth token before execution.
    reauth_resp = client.post(
        "/api/v1/auth/reauth",
        json={"password": "bob123"},
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf},
    )
    assert reauth_resp.status_code == 200
    reauth_token = reauth_resp.json()["reauth_token"]

    exec1 = client.post(
        f"/api/v1/tickets/{ticket_id}/execute",
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf, "Idempotency-Key": "idem-key-12345", "X-Reauth-Token": reauth_token},
    )
    assert exec1.status_code == 200
    body1 = exec1.json()["execution"]
    assert body1["status"] == "executed"

    # Safe retry with same key returns the original execution.
    exec_retry = client.post(
        f"/api/v1/tickets/{ticket_id}/execute",
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf, "Idempotency-Key": "idem-key-12345", "X-Reauth-Token": reauth_token},
    )
    assert exec_retry.status_code == 200
    assert exec_retry.json()["execution"]["idempotencyKey"] == "idem-key-12345"

    # Replay with a different key is denied.
    exec_replay = client.post(
        f"/api/v1/tickets/{ticket_id}/execute",
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf, "Idempotency-Key": "idem-key-OTHER", "X-Reauth-Token": reauth_token},
    )
    assert exec_replay.status_code == 409


def test_document_pdf_only_upload_and_verify_integrity():
    client = TestClient(app)
    cookies, csrf = login(client, "alice")

    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
    up = client.post(
        "/api/v1/documents/",
        cookies=cookies,
        headers={"x-csrf-token": csrf},
        data={"caseId": "C-100"},
        files={"file": ("evidence.pdf", pdf_bytes, "application/pdf")},
    )
    assert up.status_code == 200
    doc_id = up.json()["document"]["id"]

    verify = client.get(f"/api/v1/documents/{doc_id}/verify", cookies=cookies)
    assert verify.status_code == 200
    assert verify.json()["ok"] is True

    # Non-PDF is rejected.
    bad = client.post(
        "/api/v1/documents/",
        cookies=cookies,
        headers={"x-csrf-token": csrf},
        data={"caseId": "C-100"},
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert bad.status_code == 400


def test_regular_cannot_upload_for_unassigned_case():
    client = TestClient(app)
    cookies, csrf = login(client, "alice")
    pdf_bytes = b"%PDF-1.4\n%%EOF\n"

    resp = client.post(
        "/api/v1/documents/",
        cookies=cookies,
        headers={"x-csrf-token": csrf},
        data={"caseId": "C-999"},
        files={"file": ("evidence.pdf", pdf_bytes, "application/pdf")},
    )
    assert resp.status_code == 403


def test_audit_hash_chain_verifies():
    client = TestClient(app)
    cookies, _csrf = login(client, "carol")
    verify = client.get("/api/v1/audit/verify", cookies=cookies)
    assert verify.status_code == 200
    assert verify.json()["ok"] is True
