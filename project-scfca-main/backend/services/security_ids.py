"""Security identifiers and helpers.

SR-12: Audit events must be attributable to a pseudonymous user identifier.

We derive a stable pseudonymous identifier for a username using a keyed hash.
"""

from __future__ import annotations

from hashlib import sha256


def pseudonymous_actor_id(*, username: str, secret_key: str) -> str:
    raw = (username or "").strip().lower().encode("utf-8")
    key = (secret_key or "").encode("utf-8")
    return sha256(key + b"|" + raw).hexdigest()[:24]
