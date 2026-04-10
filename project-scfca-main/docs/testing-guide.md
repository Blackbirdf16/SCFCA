# SCFCA Testing Guide

> Detailed reference for the test suite. For a quick start, see the [main README](../README.md#3-test-it).

---

## Test Architecture

### No External Dependencies

All 41 tests run against **SQLite in-memory** — no PostgreSQL, Redis, or Docker needed. The test infrastructure lives in `tests/conftest.py`:

```
conftest.py
  ├── SQLite engine with StaticPool (single shared connection)
  ├── FastAPI dependency override: get_db → test session
  ├── 10 tables created at import time
  ├── 4 demo users seeded (alice, bob, eve, carol)
  │
  ├── _reset_shared_state (autouse, every test)
  │     Resets: login rate limiter, API rate limiter, MFA records
  │
  └── db_session (explicit, per test)
        Truncates all rows → re-seeds demo users → yields → no cleanup
```

### How Tests Coexist

| Test File | Uses `db_session`? | DB Mode |
|-----------|--------------------|---------|
| `test_workflows.py` | No | In-memory fallback (demo cases C-100, C-101) |
| `test_user_management.py` | Yes | Full DB (creates/queries users) |
| `test_cases_and_assets.py` | Yes | Full DB (creates cases, assets) |
| `test_tickets_phase3.py` | Yes | Full DB (creates cases → tickets → approvals → execution) |
| `test_documents_and_reports.py` | Yes | Full DB + temp filesystem for PDF bytes |
| `test_security_phase5.py` | Yes | Full DB (creates dedicated MFA test users) |

Tests with `db_session` get a **clean database** per test (all rows truncated, demo users re-seeded). Tests without it use the initial seed and in-memory service fallbacks.

---

## What Each Test Validates

### test_workflows.py (6 tests) — Core Security

| Test | Proves |
|------|--------|
| `test_login_sets_cookie_and_me_works` | JWT HttpOnly cookie issued; `/me` returns correct principal |
| `test_csrf_blocks_unsafe_without_header` | POST without X-CSRF-Token → 403 |
| `test_ticket_dual_approval_execution_...` | Full flow: create → approve×2 → assign → reauth → execute → idempotency → replay denied |
| `test_document_pdf_only_upload_and_verify` | PDF accepted, non-PDF rejected (400), SHA-256 verify |
| `test_regular_cannot_upload_for_unassigned_case` | Handler blocked from unassigned case → 403 |
| `test_audit_hash_chain_verifies` | Audit chain integrity check returns `ok: true` |

### test_user_management.py (5 tests) — FR-1, SR-4

| Test | Proves |
|------|--------|
| `test_admin_creates_user` | Admin creates user; correct fields returned |
| `test_non_admin_cannot_create_user` | Handler → 403 |
| `test_admin_lists_users` | Admin sees all seeded users |
| `test_duplicate_username_rejected` | Duplicate → 409 |
| `test_auditor_cannot_manage_users` | Auditor → 403 |

### test_cases_and_assets.py (8 tests) — FR-5 to FR-12, SR-15

| Test | Proves |
|------|--------|
| `test_admin_creates_case` | Case created with random ID, correct handler |
| `test_regular_cannot_create_case` | Handler → 403 |
| `test_case_assignment_history_recorded` | Initial assignment creates history entry |
| `test_case_reassignment_and_history` | Reassignment adds second history entry |
| `test_admin_registers_asset` | Asset created with all fields |
| `test_frozen_valuation_created` | Valuation snapshot stored and retrievable |
| `test_asset_immutability_enforced` | Modifying quantity raises ValueError (ORM listener) |
| `test_regular_cannot_register_asset` | Handler → 403 |

### test_tickets_phase3.py (8 tests) — FR-8, FR-13, FR-15, FR-18, FR-20

| Test | Proves |
|------|--------|
| `test_ticket_cancellation_by_creator` | Handler cancels open ticket → `cancelled` |
| `test_cancellation_blocked_after_full_approval` | Cancel on approved ticket → 409 |
| `test_non_creator_cannot_cancel` | Non-creator → 403 |
| `test_notes_stored_in_approval_history` | Approval notes visible in response |
| `test_rejection_notes_stored` | Rejection notes stored and returned |
| `test_conversion_request_accepted` | New ticket type works |
| `test_reassignment_ticket_full_workflow` | Execute reassignment → case handler changes |
| `test_metadata_correction_ticket_workflow` | Execute metadata update → asset notes changed |

### test_documents_and_reports.py (7 tests) — FR-23 to FR-26

| Test | Proves |
|------|--------|
| `test_document_upload_and_verify_from_db` | Upload persists; verify reads filesystem bytes |
| `test_document_download` | Downloaded bytes match original upload |
| `test_document_list_from_db` | Multiple documents listed from DB |
| `test_audit_report_pdf_download` | Valid PDF returned (starts with `%PDF-`) |
| `test_case_report_pdf_download` | Case PDF includes asset data |
| `test_report_does_not_modify_state` | Case data unchanged after report download |
| `test_auditor_can_download_audit_report` | Auditor role authorized |

### test_security_phase5.py (7 tests) — SR-5, SR-6, MU-9

| Test | Proves |
|------|--------|
| `test_mfa_setup_and_enrollment` | TOTP secret generated, code verified, MFA enabled |
| `test_mfa_login_requires_challenge` | Login → `mfa_required` → challenge → session issued |
| `test_mfa_wrong_code_rejected` | Invalid TOTP → 401 |
| `test_non_admin_cannot_setup_mfa` | Handler → 403 |
| `test_reauth_required_for_execution` | Execute without X-Reauth-Token → 403 |
| `test_reauth_with_wrong_password` | Wrong password → 401 |
| `test_reauth_success` | Correct password → valid reauth token |

---

## Common Commands

```bash
# All tests, verbose
python3 -m pytest tests/ -v

# Quick summary
python3 -m pytest tests/ -q

# Stop on first failure
python3 -m pytest tests/ -x

# By keyword
python3 -m pytest tests/ -k "mfa or reauth" -v

# Single test
python3 -m pytest tests/test_workflows.py::test_audit_hash_chain_verifies -v

# With coverage
python3 -m pytest tests/ --cov=backend -q
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: backend` | Wrong working directory | Run from project root |
| `unsupported operand type(s) for \|` | Python 3.9 type syntax | `pip3 install eval_type_backport` |
| `429 Too Many Requests` | Rate limiter from previous test | conftest resets automatically; restart pytest if stuck |
| `no such table: users` | Models not imported | Check `import backend.models` works |
| Tests pass alone but fail together | Shared state leak | conftest `_reset_shared_state` handles this |
