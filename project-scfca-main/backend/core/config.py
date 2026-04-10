"""
Configuration management for SCFCA backend using Pydantic v2+.
Defines strongly-typed, environment-driven settings for the app.
"""
from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    env: Literal["development", "test", "production"] = "development"
    app_name: str = "SCFCA"
    debug: bool = True
    database_url: str = "postgresql://user:password@localhost:5432/scfca"
    # Default is intentionally >=32 chars to avoid weak-HMAC warnings in dev/test.
    secret_key: str = "change_this_secret_to_a_32_char_minimum"

    # Security toggles (secure defaults)
    allow_legacy_auth: bool = False
    csrf_cookie_name: str = "scfca_csrf_token"
    auth_cookie_name: str = "scfca_access_token"

    # JWT hardening
    jwt_issuer: str = "scfca"
    jwt_audience: str = "scfca"
    access_token_minutes: int = 60

    # Rate limiting (PoC in-memory)
    login_max_attempts: int = 8
    login_window_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def secure_cookies(self) -> bool:
        return self.is_production

    def validate_security(self) -> None:
        # SR-15: fail loudly in production if secret looks weak/default.
        if self.is_production:
            if self.secret_key.strip() in {"change_this_secret", "change_this_secret_to_a_32_char_minimum"} or len(
                self.secret_key.strip()
            ) < 32:
                raise RuntimeError(
                    "SECRET_KEY is weak/default. Set a strong SECRET_KEY (>=32 chars) for production."
                )

settings = Settings()

# Validate at import time so misconfiguration fails early.
settings.validate_security()
