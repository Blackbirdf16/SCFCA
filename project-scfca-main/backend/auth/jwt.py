"""JWT helpers for SCFCA.

PoC-friendly but real security primitive:
- HS256 signed JWTs with expiry.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets

import jwt


def create_access_token(
    *,
    subject: str,
    role: str,
    secret_key: str,
    issuer: str,
    audience: str,
    expires_minutes: int = 60,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iss": issuer,
        "aud": audience,
        "jti": secrets.token_urlsafe(16),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_access_token(token: str, *, secret_key: str, issuer: str, audience: str) -> dict:
    return jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
        issuer=issuer,
        audience=audience,
        options={"require": ["exp", "iat", "sub", "role", "iss", "aud", "jti"]},
    )
