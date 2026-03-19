"""
Configuration management for SCFCA backend using Pydantic v2+.
Defines strongly-typed, environment-driven settings for the app.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""
    app_name: str = "SCFCA"
    debug: bool = True
    database_url: str = "postgresql://user:password@localhost:5432/scfca"
    secret_key: str = "change_this_secret"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
