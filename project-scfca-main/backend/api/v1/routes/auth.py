"""Authentication endpoints for SCFCA backend.

SR-5:  MFA (TOTP) for privileged roles.
SR-6:  Re-authentication for sensitive actions.
SR-7:  Session traceability via JWT jti claim.
SR-19: Brute-force resistance via rate limiting.
SR-20: Token revocation on logout.
"""

from __future__ import annotations

import secrets
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.auth.dependencies import Principal, get_current_principal, get_optional_principal, require_role
from backend.auth.jwt import create_access_token, decode_access_token
from backend.auth.schemas import LoginRequest, LoginResponse, MeResponse, Role
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.logging import logger
from backend.repositories.user_repo import USER_REPO
from backend.services.audit_log import AUDIT_LOG
from backend.services.mfa_service import generate_secret, get_provisioning_uri, verify_totp
from backend.services.rate_limit import get_login_rate_limiter
from backend.services.security_ids import pseudonymous_actor_id
from backend.services.session_store import SESSION_STORE

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Demo users fallback (PoC/test mode when DB is unavailable)
# ---------------------------------------------------------------------------
_DEMO_USERS: dict[str, dict[str, str]] = {
    "alice": {"password_hash": pwd_context.hash("alice123"), "role": Role.regular.value},
    "bob": {"password_hash": pwd_context.hash("bob123"), "role": Role.administrator.value},
    "eve": {"password_hash": pwd_context.hash("eve123"), "role": Role.administrator.value},
    "carol": {"password_hash": pwd_context.hash("carol123"), "role": Role.auditor.value},
}


def _authenticate(username: str, password: str, db: Session | None = None) -> tuple[str, Role] | None:
    """Authenticate user against DB first, then fall back to demo users."""
    uname = (username or "").strip().lower()
    if not uname or not password:
        return None

    if db is not None:
        try:
            user = USER_REPO.get_by_username(db, uname)
            if user and user.is_active and pwd_context.verify(password, user.password_hash):
                return uname, Role(user.role.value if hasattr(user.role, "value") else user.role)
            if user:
                return None
        except Exception:
            pass

    record = _DEMO_USERS.get(uname)
    if not record:
        return None
    if not pwd_context.verify(password, record["password_hash"]):
        return None
    return uname, Role(record["role"])


def _get_db_or_none() -> Session | None:
    """Get a DB session, respecting FastAPI dependency overrides."""
    from backend.main import app as _app
    override = _app.dependency_overrides.get(get_db)
    provider = override if override else get_db
    try:
        return next(provider())
    except Exception:
        return None


def _check_mfa_enabled(username: str, db: Session | None = None) -> bool:
    """Check if user has MFA enabled. Always uses a fresh session."""
    fresh_db = _get_db_or_none()
    if fresh_db is None:
        return False
    try:
        from backend.models.mfa import UserMFA
        from sqlalchemy import text
        # Use raw SQL to avoid any ORM caching
        user = USER_REPO.get_by_username(fresh_db, username)
        if not user:
            return False
        result = fresh_db.execute(
            text("SELECT COUNT(*) FROM user_mfa WHERE user_id = :uid AND is_enabled = 1"),
            {"uid": str(user.id)},
        )
        count = result.scalar() or 0
        return count > 0
    except Exception:
        return False
    finally:
        fresh_db.close()


def _get_mfa_secret(username: str, db: Session) -> str | None:
    """Get TOTP secret for a user. Returns None if not enrolled."""
    try:
        from backend.models.mfa import UserMFA
        user = USER_REPO.get_by_username(db, username)
        if not user:
            return None
        mfa = db.query(UserMFA).filter(UserMFA.user_id == user.id).first()
        return mfa.totp_secret if mfa else None
    except Exception:
        return None


def _issue_session(auth_username: str, role: Role, response: Response) -> str:
    """Create JWT, set cookies, return token."""
    token = create_access_token(
        subject=auth_username,
        role=role.value,
        secret_key=settings.secret_key,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        expires_minutes=settings.access_token_minutes,
    )
    csrf_token = secrets.token_urlsafe(32)

    response.set_cookie(
        key=settings.auth_cookie_name, value=token, httponly=True,
        samesite="lax", secure=settings.secure_cookies,
        max_age=settings.access_token_minutes * 60, path="/",
    )
    response.set_cookie(
        key=settings.csrf_cookie_name, value=csrf_token, httponly=False,
        samesite="lax", secure=settings.secure_cookies,
        max_age=settings.access_token_minutes * 60, path="/",
    )
    return token


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class MFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str

class MFAVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)

class MFAChallengeRequest(BaseModel):
    mfa_token: str
    code: str = Field(..., min_length=6, max_length=6)

class ReauthRequest(BaseModel):
    password: str


# ---------------------------------------------------------------------------
# Login (SR-5: MFA-aware)
# ---------------------------------------------------------------------------

@router.post("/login", summary="User login", tags=["auth"])
def login(payload: LoginRequest, response: Response, request: Request):
    username = (payload.username or "").strip().lower()
    password = payload.password or ""
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

    client_host = request.client.host if request.client else "unknown"
    limiter = get_login_rate_limiter(
        max_attempts=settings.login_max_attempts,
        window_seconds=settings.login_window_seconds,
    )
    rl = limiter.check(f"login:{client_host}:{username}")
    if not rl.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(rl.retry_after_seconds)},
        )

    db = _get_db_or_none()
    try:
        authenticated = _authenticate(username, password, db)
    finally:
        if db is not None:
            db.close()

    if not authenticated:
        AUDIT_LOG.append(
            actor_id=pseudonymous_actor_id(username=username or "unknown", secret_key=settings.secret_key),
            event_type="auth", action="login_failed", entity_type="user",
            entity_id=username or None,
            details={"reason": "invalid_credentials", "client": client_host},
        )
        logger.info("security_event login_failed user=%s client=%s", username, client_host)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    auth_username, role = authenticated

    # SR-5: Check if MFA is enabled for this user
    db2 = _get_db_or_none()
    mfa_enabled = False
    try:
        mfa_enabled = _check_mfa_enabled(auth_username, db2)
    finally:
        if db2 is not None:
            db2.close()

    if mfa_enabled:
        # Issue a short-lived MFA token (not a full session)
        mfa_token = create_access_token(
            subject=auth_username, role="mfa_pending",
            secret_key=settings.secret_key,
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            expires_minutes=5,
        )
        AUDIT_LOG.append(
            actor_id=pseudonymous_actor_id(username=auth_username, secret_key=settings.secret_key),
            event_type="auth", action="mfa_challenge_issued", entity_type="user",
            entity_id=auth_username,
            details={"client": client_host},
        )
        return {"mfa_required": True, "mfa_token": mfa_token, "username": auth_username}

    # No MFA — issue full session directly
    _issue_session(auth_username, role, response)

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=auth_username, secret_key=settings.secret_key),
        event_type="auth", action="login_succeeded", entity_type="user",
        entity_id=auth_username,
        details={"role": role.value, "client": client_host},
    )
    logger.info("security_event login_succeeded user=%s role=%s", auth_username, role.value)

    return LoginResponse(username=auth_username, role=role)


# ---------------------------------------------------------------------------
# MFA Endpoints (SR-5)
# ---------------------------------------------------------------------------

@router.post("/mfa/setup", summary="Setup MFA (generate TOTP secret)", tags=["auth"])
def mfa_setup(
    principal: Annotated[Principal, Depends(require_role(Role.administrator))],
    db: Session = Depends(get_db),
):
    """Generate a TOTP secret for MFA enrollment. Admin only. SR-5."""
    from backend.models.mfa import UserMFA

    user = USER_REPO.get_by_username(db, principal.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    secret = generate_secret()
    uri = get_provisioning_uri(secret, principal.username)

    # Upsert MFA record (not yet enabled)
    existing = db.query(UserMFA).filter(UserMFA.user_id == user.id).first()
    if existing:
        existing.totp_secret = secret
        existing.is_enabled = False
    else:
        db.add(UserMFA(user_id=user.id, totp_secret=secret, is_enabled=False))
    db.commit()

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="auth", action="mfa_setup_initiated", entity_type="user",
        entity_id=principal.username,
    )
    return MFASetupResponse(secret=secret, provisioning_uri=uri)


@router.post("/mfa/verify", summary="Verify TOTP and enable MFA", tags=["auth"])
def mfa_verify(
    payload: MFAVerifyRequest,
    principal: Annotated[Principal, Depends(require_role(Role.administrator))],
    db: Session = Depends(get_db),
):
    """Verify a TOTP code and enable MFA for the user. SR-5."""
    from backend.models.mfa import UserMFA

    user = USER_REPO.get_by_username(db, principal.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    mfa = db.query(UserMFA).filter(UserMFA.user_id == user.id).first()
    if not mfa:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not set up. Call /mfa/setup first.")

    if not verify_totp(mfa.totp_secret, payload.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

    mfa.is_enabled = True
    db.commit()

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="auth", action="mfa_enabled", entity_type="user",
        entity_id=principal.username,
    )
    return {"status": "mfa_enabled"}


@router.post("/mfa/challenge", summary="Complete MFA login challenge", tags=["auth"])
def mfa_challenge(payload: MFAChallengeRequest, response: Response, request: Request):
    """Submit TOTP code with mfa_token to complete login. SR-5."""
    try:
        token_payload = decode_access_token(
            token=payload.mfa_token,
            secret_key=settings.secret_key,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired MFA token")

    if token_payload.get("role") != "mfa_pending":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA token type")

    username = token_payload.get("sub", "")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA token")

    db = _get_db_or_none()
    if db is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database unavailable")

    try:
        secret = _get_mfa_secret(username, db)
        if not secret:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not configured")

        if not verify_totp(secret, payload.code):
            AUDIT_LOG.append(
                actor_id=pseudonymous_actor_id(username=username, secret_key=settings.secret_key),
                event_type="auth", action="mfa_challenge_failed", entity_type="user",
                entity_id=username,
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

        # MFA verified — determine actual role and issue session
        user = USER_REPO.get_by_username(db, username)
        role = Role(user.role.value if hasattr(user.role, "value") else user.role)
    finally:
        db.close()

    _issue_session(username, role, response)
    client_host = request.client.host if request.client else "unknown"

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=username, secret_key=settings.secret_key),
        event_type="auth", action="login_succeeded_mfa", entity_type="user",
        entity_id=username,
        details={"role": role.value, "client": client_host, "mfa": True},
    )
    logger.info("security_event login_succeeded_mfa user=%s role=%s", username, role.value)

    return LoginResponse(username=username, role=role)


# ---------------------------------------------------------------------------
# Re-Authentication (SR-6)
# ---------------------------------------------------------------------------

@router.post("/reauth", summary="Re-authenticate for sensitive actions", tags=["auth"])
def reauth(
    payload: ReauthRequest,
    principal: Annotated[Principal, Depends(get_current_principal)],
):
    """Re-authenticate with password to obtain a short-lived reauth token. SR-6."""
    db = _get_db_or_none()
    try:
        authenticated = _authenticate(principal.username, payload.password, db)
    finally:
        if db is not None:
            db.close()

    if not authenticated:
        AUDIT_LOG.append(
            actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
            event_type="auth", action="reauth_failed", entity_type="user",
            entity_id=principal.username,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    # Issue a short-lived reauth token (5 min)
    reauth_token = create_access_token(
        subject=principal.username, role="reauth",
        secret_key=settings.secret_key,
        issuer=settings.jwt_issuer, audience=settings.jwt_audience,
        expires_minutes=5,
    )

    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="auth", action="reauth_succeeded", entity_type="user",
        entity_id=principal.username,
    )
    return {"reauth_token": reauth_token}


# ---------------------------------------------------------------------------
# Logout, Me, CSRF (unchanged)
# ---------------------------------------------------------------------------

@router.post("/logout", summary="Logout", tags=["auth"])
def logout(
    request: Request,
    response: Response,
    principal: Annotated[Optional[Principal], Depends(get_optional_principal)] = None,
):
    token = request.cookies.get(settings.auth_cookie_name)
    if token:
        try:
            payload = decode_access_token(
                token=token, secret_key=settings.secret_key,
                issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            )
            jti = str(payload.get("jti") or "")
            exp = int(payload.get("exp") or 0)
            if jti and exp:
                SESSION_STORE.revoke(jti=jti, exp=exp)
        except Exception:
            pass

    response.delete_cookie(settings.auth_cookie_name, path="/")
    response.delete_cookie(settings.csrf_cookie_name, path="/")
    actor = principal.username if principal else "unknown"
    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=actor, secret_key=settings.secret_key),
        event_type="auth", action="logout", entity_type="user",
        entity_id=principal.username if principal else None, details={},
    )
    return {"status": "ok"}


@router.get("/me", summary="Current principal", tags=["auth"])
def me(principal: Annotated[Principal, Depends(get_current_principal)]) -> MeResponse:
    return MeResponse(username=principal.username, role=principal.role)


@router.get("/csrf", summary="Rotate CSRF token", tags=["auth"])
def csrf(
    response: Response,
    principal: Annotated[Principal, Depends(get_current_principal)],
):
    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        key=settings.csrf_cookie_name, value=csrf_token, httponly=False,
        samesite="lax", secure=settings.secure_cookies,
        max_age=settings.access_token_minutes * 60, path="/",
    )
    AUDIT_LOG.append(
        actor_id=pseudonymous_actor_id(username=principal.username, secret_key=settings.secret_key),
        event_type="auth", action="csrf_rotated", details={},
    )
    return {"csrfToken": csrf_token}
