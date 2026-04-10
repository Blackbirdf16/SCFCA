# Phase 5 — Advanced Security Controls

**Status:** Complete
**Date:** 2026-04-09
**Covers:** SR-5, SR-6, MU-1, MU-9

---

## 1. Objective

Close the three critical security gaps identified in the thesis threat model: TOTP-based MFA for admin login (SR-5), re-authentication for sensitive custody operations (SR-6), and general API rate limiting to mitigate denial-of-service attacks (MU-9).

---

## 2. Requirements Addressed

| ID | Requirement | How Addressed |
|----|------------|---------------|
| **SR-5** | MFA for privileged roles | TOTP via `pyotp`; admin setup/verify/challenge flow; login returns `mfa_required` when enabled |
| **SR-6** | Re-authentication for sensitive actions | `POST /auth/reauth` → short-lived token; validated via `X-Reauth-Token` header on ticket execution |
| **MU-1** | Unauthorized access mitigation | MFA adds second factor; password alone insufficient for admin access |
| **MU-9** | Denial of service mitigation | General API rate limiting: 120 read/min, 60 write/min per IP |

---

## 3. MFA Implementation (SR-5)

### Login Flow

```
Without MFA:  POST /login → JWT cookie + CSRF cookie (unchanged)

With MFA:     POST /login → {"mfa_required": true, "mfa_token": "<5min JWT>"}
              POST /mfa/challenge {mfa_token, code} → JWT cookie + CSRF cookie
```

The `mfa_token` is a short-lived JWT (5 min) with `role: "mfa_pending"`. It proves the password was verified but cannot access any protected endpoint.

### Enrollment Flow

```
POST /auth/mfa/setup    → {secret, provisioning_uri}     (admin only)
POST /auth/mfa/verify   → {status: "mfa_enabled"}        (verify TOTP code)
```

### Database

```sql
CREATE TABLE user_mfa (
    user_id    CHAR(36)    PRIMARY KEY REFERENCES users(id),
    totp_secret VARCHAR(64) NOT NULL,
    is_enabled  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

---

## 4. Re-Authentication (SR-6)

### Flow

```
POST /auth/reauth {password} → {reauth_token: "<5min JWT>"}

Then on sensitive endpoints:
  Header: X-Reauth-Token: <reauth_token>
```

### Applied To

| Endpoint | Action |
|----------|--------|
| `POST /tickets/{id}/execute` | Custody execution (DB path only) |

Additional endpoints (case reassignment, role changes) can be wired in Phase 6.

---

## 5. Rate Limiting (MU-9)

### Middleware

`RateLimitMiddleware` in `backend/middleware/rate_limit.py`:
- **Read endpoints** (GET/HEAD/OPTIONS): 120 req/min per IP
- **Write endpoints** (POST/PUT/PATCH/DELETE): 60 req/min per IP
- **Health endpoint** exempted
- **Login** has its own stricter limiter (8 req/60s)

---

## 6. Files Created

| File | Purpose |
|------|---------|
| `backend/models/mfa.py` | UserMFA ORM model |
| `backend/services/mfa_service.py` | TOTP generation/verification via pyotp |
| `backend/auth/reauth.py` | Re-auth dependency + token validation |
| `backend/middleware/rate_limit.py` | General API rate limiting middleware |
| `backend/alembic/versions/005_mfa.py` | Migration: user_mfa table |
| `tests/test_security_phase5.py` | 7 security tests |

## 7. Files Modified

| File | Change |
|------|--------|
| `backend/models/__init__.py` | Registered UserMFA |
| `backend/main.py` | Registered RateLimitMiddleware |
| `backend/api/v1/routes/auth.py` | MFA endpoints, reauth endpoint, MFA-aware login |
| `backend/api/v1/routes/tickets.py` | Reauth required on execute (DB path) |
| `backend/requirements.txt` | Added pyotp |
| `tests/conftest.py` | Rate limiter + MFA state reset between tests |
| `tests/test_workflows.py` | Added reauth token to execute calls |
| `tests/test_tickets_phase3.py` | Added reauth token to execution tests |

---

## 8. Test Coverage

### New Tests (Phase 5) — 7 tests

| Test | Requirement | Validates |
|------|-------------|-----------|
| `test_mfa_setup_and_enrollment` | SR-5 | Admin generates secret, verifies code, MFA enabled |
| `test_mfa_login_requires_challenge` | SR-5 | Login with MFA → challenge → session issued |
| `test_mfa_wrong_code_rejected` | SR-5 | Invalid TOTP → 401 |
| `test_non_admin_cannot_setup_mfa` | SR-5 | Regular user → 403 |
| `test_reauth_required_for_execution` | SR-6 | Execute without reauth → 403 |
| `test_reauth_with_wrong_password` | SR-6 | Wrong password → 401 |
| `test_reauth_success` | SR-6 | Correct password → valid reauth token |

### Full Suite

```
41 passed — 6 original + 5 Phase 1 + 8 Phase 2 + 8 Phase 3 + 7 Phase 4 + 7 Phase 5
```
