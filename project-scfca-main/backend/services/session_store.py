"""In-memory session revocation store (PoC).

Stores revoked JWT IDs (jti) until their token expiry.
This enables logout to invalidate a stolen access token immediately.

Demo-safe only: not shared across processes and not persistent.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass(frozen=True)
class RevokedToken:
    jti: str
    exp: int


class SessionStore:
    def __init__(self) -> None:
        self._revoked: dict[str, int] = {}

    def revoke(self, jti: str, exp: int) -> None:
        if not jti or not isinstance(exp, int):
            return
        self._revoked[jti] = exp

    def is_revoked(self, jti: str) -> bool:
        self._prune_expired()
        return jti in self._revoked

    def _prune_expired(self) -> None:
        now = int(time())
        expired = [jti for jti, exp in self._revoked.items() if exp <= now]
        for jti in expired:
            self._revoked.pop(jti, None)


SESSION_STORE = SessionStore()
