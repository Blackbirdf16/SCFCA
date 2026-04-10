"""Tests for complete ticket workflow (Phase 3).

FR-8:  Reassignment via approved ticket.
FR-13: Metadata correction via approved ticket.
FR-15: All 6 ticket types.
FR-18: Mandatory notes on approve/reject.
FR-20: Ticket cancellation by handler.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.main import app
from tests.conftest import TestSession

USERS = {
    "alice": {"username": "alice", "password": "alice123"},
    "bob": {"username": "bob", "password": "bob123"},
    "eve": {"username": "eve", "password": "eve123"},
    "carol": {"username": "carol", "password": "carol123"},
}


@pytest.fixture(autouse=True)
def _db(db_session):
    """Use the shared DB fixture from conftest."""
    yield


def login(client: TestClient, username: str):
    resp = client.post("/api/v1/auth/login", json=USERS[username])
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    csrf = resp.cookies.get(settings.csrf_cookie_name)
    assert csrf
    return resp.cookies, csrf


def _create_case_and_ticket(client, ticket_type="transfer_request", parameters=None):
    """Helper: admin creates case, handler creates ticket."""
    bob_cookies, bob_csrf = login(client, "bob")

    # Create case assigned to alice
    case = client.post(
        "/api/v1/cases/",
        json={"title": "Test case", "wallet_ref": "WLT-TEST", "handler_username": "alice"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    ).json()["case"]

    # Alice creates ticket
    alice_cookies, alice_csrf = login(client, "alice")
    payload = {
        "caseId": case["id"],
        "ticketType": ticket_type,
        "description": f"Test {ticket_type}",
    }
    if parameters:
        payload["parameters"] = parameters

    ticket = client.post(
        "/api/v1/tickets/", json=payload,
        cookies=alice_cookies, headers={"x-csrf-token": alice_csrf},
    )
    assert ticket.status_code == 200, ticket.text
    return case, ticket.json()["ticket"]


def _dual_approve(client, ticket_id):
    """Helper: bob approves stage 1, eve approves stage 2."""
    bob_cookies, bob_csrf = login(client, "bob")
    a1 = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        json={"notes": "Stage 1 approved"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    assert a1.status_code == 200, a1.text

    eve_cookies, eve_csrf = login(client, "eve")
    a2 = client.post(
        f"/api/v1/tickets/{ticket_id}/approve",
        json={"notes": "Stage 2 approved"},
        cookies=eve_cookies, headers={"x-csrf-token": eve_csrf},
    )
    assert a2.status_code == 200, a2.text
    return a2.json()["ticket"]


# ---------------------------------------------------------------------------
# FR-20: Ticket Cancellation
# ---------------------------------------------------------------------------

def test_ticket_cancellation_by_creator():
    """FR-20: Handler can cancel their own open ticket."""
    client = TestClient(app)
    _, ticket = _create_case_and_ticket(client)

    alice_cookies, alice_csrf = login(client, "alice")
    resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/cancel",
        json={"reason": "No longer needed"},
        cookies=alice_cookies, headers={"x-csrf-token": alice_csrf},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["ticket"]["status"] == "cancelled"


def test_cancellation_blocked_after_full_approval():
    """FR-20: Cannot cancel a fully approved ticket."""
    client = TestClient(app)
    _, ticket = _create_case_and_ticket(client)
    _dual_approve(client, ticket["id"])

    alice_cookies, alice_csrf = login(client, "alice")
    resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/cancel",
        json={"reason": "Too late"},
        cookies=alice_cookies, headers={"x-csrf-token": alice_csrf},
    )
    assert resp.status_code == 409


def test_non_creator_cannot_cancel():
    """FR-20: Only the ticket creator can cancel."""
    client = TestClient(app)
    _, ticket = _create_case_and_ticket(client)

    bob_cookies, bob_csrf = login(client, "bob")
    resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/cancel",
        json={"reason": "Not mine"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# FR-18: Mandatory Notes
# ---------------------------------------------------------------------------

def test_notes_stored_in_approval_history():
    """FR-18: Notes are stored and returned in approval history."""
    client = TestClient(app)
    _, ticket = _create_case_and_ticket(client)

    bob_cookies, bob_csrf = login(client, "bob")
    resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/approve",
        json={"notes": "Documentation verified, proceeding."},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    assert resp.status_code == 200
    history = resp.json()["ticket"]["approvalHistory"]
    assert len(history) >= 1
    assert history[0]["notes"] == "Documentation verified, proceeding."


def test_rejection_notes_stored():
    """FR-18: Rejection notes are stored."""
    client = TestClient(app)
    _, ticket = _create_case_and_ticket(client)

    bob_cookies, bob_csrf = login(client, "bob")
    resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/reject",
        json={"notes": "Insufficient evidence. Resubmit with court order."},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    assert resp.status_code == 200
    assert resp.json()["ticket"]["status"] == "rejected"
    history = resp.json()["ticket"]["approvalHistory"]
    assert any("Insufficient evidence" in h.get("notes", "") for h in history)


# ---------------------------------------------------------------------------
# FR-15: New Ticket Types
# ---------------------------------------------------------------------------

def test_conversion_request_accepted():
    """FR-15: conversion_request ticket type is accepted."""
    client = TestClient(app)
    _, ticket = _create_case_and_ticket(client, ticket_type="conversion_request")
    assert ticket["ticketType"] == "conversion_request"
    assert ticket["status"] == "pending_review"


def test_reassignment_ticket_full_workflow():
    """FR-8, FR-15: Reassignment ticket triggers case handler change on execution."""
    client = TestClient(app)

    bob_cookies, bob_csrf = login(client, "bob")

    # Create case assigned to alice
    case = client.post(
        "/api/v1/cases/",
        json={"title": "Reassignment test", "wallet_ref": "WLT-REASSIGN2", "handler_username": "alice"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    ).json()["case"]

    # Alice creates reassignment ticket
    alice_cookies, alice_csrf = login(client, "alice")
    ticket = client.post(
        "/api/v1/tickets/",
        json={
            "caseId": case["id"],
            "ticketType": "reassignment",
            "description": "Reassign to eve",
            "parameters": {"newHandlerUsername": "eve"},
        },
        cookies=alice_cookies, headers={"x-csrf-token": alice_csrf},
    ).json()["ticket"]

    # Dual approve
    _dual_approve(client, ticket["id"])

    # Assign to bob for execution
    bob_cookies, bob_csrf = login(client, "bob")
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/assign",
        json={"assignedTo": "bob"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )

    # SR-6: Get reauth token
    reauth = client.post(
        "/api/v1/auth/reauth", json={"password": "bob123"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    reauth_token = reauth.json()["reauth_token"]

    # Execute — should trigger case reassignment
    exec_resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/execute",
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf, "Idempotency-Key": "reassign-key-001", "X-Reauth-Token": reauth_token},
    )
    assert exec_resp.status_code == 200, exec_resp.text
    assert "case_reassigned" in exec_resp.json()["execution"]["result"]

    # Verify case handler changed
    case_detail = client.get(f"/api/v1/cases/{case['id']}", cookies=bob_cookies)
    assert case_detail.json()["case"]["handler"] == "eve"


def test_metadata_correction_ticket_workflow():
    """FR-13, FR-15: Metadata correction ticket updates asset notes on execution."""
    client = TestClient(app)

    bob_cookies, bob_csrf = login(client, "bob")

    # Create case + asset
    case = client.post(
        "/api/v1/cases/",
        json={"title": "Metadata test", "wallet_ref": "WLT-META", "handler_username": "alice"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    ).json()["case"]

    asset = client.post(
        "/api/v1/assets/",
        json={"caseId": case["id"], "symbol": "BTC", "assetType": "native", "quantity": 5.0},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    ).json()["asset"]

    # Alice creates metadata correction ticket
    alice_cookies, alice_csrf = login(client, "alice")
    ticket = client.post(
        "/api/v1/tickets/",
        json={
            "caseId": case["id"],
            "ticketType": "metadata_correction",
            "description": "Update notes on seized BTC",
            "parameters": {"assetId": asset["id"], "notes": "Corrected provenance info"},
        },
        cookies=alice_cookies, headers={"x-csrf-token": alice_csrf},
    ).json()["ticket"]

    # Dual approve + assign + execute
    _dual_approve(client, ticket["id"])

    bob_cookies, bob_csrf = login(client, "bob")
    client.patch(
        f"/api/v1/tickets/{ticket['id']}/assign",
        json={"assignedTo": "bob"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )

    # SR-6: Get reauth token
    reauth = client.post(
        "/api/v1/auth/reauth", json={"password": "bob123"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    reauth_token = reauth.json()["reauth_token"]

    exec_resp = client.post(
        f"/api/v1/tickets/{ticket['id']}/execute",
        cookies=bob_cookies,
        headers={"x-csrf-token": bob_csrf, "Idempotency-Key": "metadata-key-001", "X-Reauth-Token": reauth_token},
    )
    assert exec_resp.status_code == 200, exec_resp.text
    assert "metadata_updated" in exec_resp.json()["execution"]["result"]

    # Verify asset notes updated
    asset_detail = client.get(f"/api/v1/assets/{asset['id']}", cookies=bob_cookies)
    assert asset_detail.json()["asset"]["notes"] == "Corrected provenance info"
