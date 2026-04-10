"""Tests for document persistence and server-side reports (Phase 4).

FR-23: Document integrity — upload, verify, download.
FR-24: Audit report PDF download.
FR-25: Case report PDF download.
FR-26: Reports are informational (no state mutation).
SR-16: Document integrity verification.
NFR-4: Persistent storage.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.config import settings
from backend.main import app
from backend.services.file_storage import FILE_STORAGE
from tests.conftest import TestSession

USERS = {
    "alice": {"username": "alice", "password": "alice123"},
    "bob": {"username": "bob", "password": "bob123"},
    "eve": {"username": "eve", "password": "eve123"},
    "carol": {"username": "carol", "password": "carol123"},
}

PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n"


@pytest.fixture(autouse=True)
def _db(db_session, tmp_path):
    """Use shared DB fixture + temporary file storage."""
    # Point file storage to temp dir so tests don't pollute real data
    FILE_STORAGE._base = tmp_path / "documents"
    FILE_STORAGE._base.mkdir(parents=True, exist_ok=True)
    yield


def login(client: TestClient, username: str):
    resp = client.post("/api/v1/auth/login", json=USERS[username])
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    csrf = resp.cookies.get(settings.csrf_cookie_name)
    assert csrf
    return resp.cookies, csrf


def _create_case(client):
    """Helper: admin creates a case assigned to alice."""
    bob_cookies, bob_csrf = login(client, "bob")
    resp = client.post(
        "/api/v1/cases/",
        json={"title": "Doc test case", "wallet_ref": "WLT-DOC", "handler_username": "alice"},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )
    return resp.json()["case"]


# ---------------------------------------------------------------------------
# Document Tests
# ---------------------------------------------------------------------------

def test_document_upload_and_verify_from_db():
    """FR-23, SR-16, NFR-4: Upload persists in DB, verify reads from filesystem."""
    client = TestClient(app)
    case = _create_case(client)

    alice_cookies, alice_csrf = login(client, "alice")
    up = client.post(
        "/api/v1/documents/",
        cookies=alice_cookies, headers={"x-csrf-token": alice_csrf},
        data={"caseId": case["id"]},
        files={"file": ("evidence.pdf", PDF_BYTES, "application/pdf")},
    )
    assert up.status_code == 200, up.text
    doc = up.json()["document"]
    assert doc["id"].startswith("DOC-")
    assert "sha256:" in doc["hash"]

    # Verify integrity
    verify = client.get(f"/api/v1/documents/{doc['id']}/verify", cookies=alice_cookies)
    assert verify.status_code == 200
    assert verify.json()["ok"] is True


def test_document_download():
    """FR-23: Download returns original PDF bytes."""
    client = TestClient(app)
    case = _create_case(client)

    bob_cookies, bob_csrf = login(client, "bob")
    up = client.post(
        "/api/v1/documents/",
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
        data={"caseId": case["id"]},
        files={"file": ("report.pdf", PDF_BYTES, "application/pdf")},
    )
    doc_id = up.json()["document"]["id"]

    dl = client.get(f"/api/v1/documents/{doc_id}/download", cookies=bob_cookies)
    assert dl.status_code == 200
    assert dl.headers["content-type"] == "application/pdf"
    assert dl.content == PDF_BYTES


def test_document_list_from_db():
    """NFR-4: Listed documents come from DB."""
    client = TestClient(app)
    case = _create_case(client)

    bob_cookies, bob_csrf = login(client, "bob")
    client.post(
        "/api/v1/documents/",
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
        data={"caseId": case["id"]},
        files={"file": ("a.pdf", PDF_BYTES, "application/pdf")},
    )
    client.post(
        "/api/v1/documents/",
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
        data={"caseId": case["id"]},
        files={"file": ("b.pdf", PDF_BYTES, "application/pdf")},
    )

    resp = client.get("/api/v1/documents/", cookies=bob_cookies)
    assert resp.status_code == 200
    docs = resp.json()["documents"]
    assert len(docs) >= 2


# ---------------------------------------------------------------------------
# Report Tests
# ---------------------------------------------------------------------------

def test_audit_report_pdf_download():
    """FR-24: Admin can download audit report as PDF."""
    client = TestClient(app)
    bob_cookies, bob_csrf = login(client, "bob")

    resp = client.get("/api/v1/reports/audit", cookies=bob_cookies)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


def test_case_report_pdf_download():
    """FR-25: Admin can download case report with assets."""
    client = TestClient(app)
    bob_cookies, bob_csrf = login(client, "bob")

    # Create case + asset
    case = _create_case(client)
    client.post(
        "/api/v1/assets/",
        json={"caseId": case["id"], "symbol": "BTC", "assetType": "native", "quantity": 5.0},
        cookies=bob_cookies, headers={"x-csrf-token": bob_csrf},
    )

    resp = client.get(f"/api/v1/reports/case/{case['id']}", cookies=bob_cookies)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


def test_report_does_not_modify_state():
    """FR-26: Report generation doesn't modify any case/ticket/asset data."""
    client = TestClient(app)
    bob_cookies, bob_csrf = login(client, "bob")
    case = _create_case(client)

    # Get case details before report
    before = client.get(f"/api/v1/cases/{case['id']}", cookies=bob_cookies).json()

    # Download report
    client.get(f"/api/v1/reports/case/{case['id']}", cookies=bob_cookies)

    # Get case details after report
    after = client.get(f"/api/v1/cases/{case['id']}", cookies=bob_cookies).json()

    assert before["case"]["custodyStatus"] == after["case"]["custodyStatus"]
    assert before["case"]["handler"] == after["case"]["handler"]


def test_auditor_can_download_audit_report():
    """FR-24: Auditor can access audit report."""
    client = TestClient(app)
    carol_cookies, _ = login(client, "carol")

    resp = client.get("/api/v1/reports/audit", cookies=carol_cookies)
    assert resp.status_code == 200
    assert resp.content[:5] == b"%PDF-"
