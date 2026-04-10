"""TOTP-based MFA service for SCFCA.

SR-5: Multi-factor authentication for privileged roles.

Uses pyotp for TOTP generation and verification.
"""

from __future__ import annotations

import pyotp


ISSUER_NAME = "SCFCA"


def generate_secret() -> str:
    """Generate a new base32 TOTP secret."""
    return pyotp.random_base32()


def get_provisioning_uri(secret: str, username: str) -> str:
    """Return an otpauth:// URI for QR code enrollment."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=ISSUER_NAME)


def verify_totp(secret: str, code: str) -> bool:
    """Verify a 6-digit TOTP code against the secret.

    Accepts codes within a 1-step window (±30 seconds) for clock skew tolerance.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def get_current_code(secret: str) -> str:
    """Return the current valid TOTP code. Used only in tests."""
    totp = pyotp.TOTP(secret)
    return totp.now()
