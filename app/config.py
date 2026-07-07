from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram
    bot_token: str
    support_username: str = "support"
    support_chat_link: str = "https://t.me/support"

    # Database (Railway injects DATABASE_URL automatically when Postgres plugin is attached)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/digitalchecker"

    # Redis (Railway injects REDIS_URL automatically when Redis plugin is attached)
    redis_url: str = "redis://localhost:6379/0"

    # External APIs
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key: str | None = None  # optional, for pro tier / higher rate limits

    # Caching
    cache_ttl_seconds: int = 30
    coin_list_ttl_seconds: int = 3600

    # Rate limiting
    rate_limit_per_second: float = 1.0

    # Alerts worker
    alert_check_interval_seconds: int = 60

    # Misc
    log_level: str = "INFO"
    default_language: str = "fa"

    @field_validator("database_url", "redis_url")
    @classmethod
    def validate_connection_url(cls, v: str, info) -> str:
        """
        Fail fast with a clear message instead of letting SQLAlchemy raise
        'Could not parse SQLAlchemy URL from string ""' deep inside alembic/env.py.

        This catches two common Railway misconfigurations:
        1. The variable reference wasn't resolved and is still literal text,
           e.g. '{{Postgres.DATABASE_URL}}' (missing leading '$').
        2. The variable reference resolved to an empty string, which happens
           when the referenced service name doesn't match exactly (case-sensitive)
           or the reference was typed manually instead of picked from Railway's
           '${{' autocomplete dropdown.
        """
        if not v or not v.strip():
            raise ValueError(
                f"{info.field_name} is empty. This usually means the Railway "
                f"variable reference (e.g. ${{{{Postgres.DATABASE_URL}}}}) resolved "
                f"to nothing. In the Railway dashboard, go to your service's "
                f"Variables tab, edit {info.field_name.upper()}, type '${{{{' and "
                f"pick the service + variable from the autocomplete dropdown "
                f"instead of typing it manually — the service name must match "
                f"exactly, including case."
            )
        if "{{" in v or "}}" in v:
            raise ValueError(
                f"{info.field_name} still contains an unresolved Railway reference "
                f"({v!r}). The value must start with '$', e.g. "
                f"${{{{Postgres.DATABASE_URL}}}} not {{{{Postgres.DATABASE_URL}}}}."
            )
        return v.strip()


settings = Settings()
