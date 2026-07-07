from __future__ import annotations

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


settings = Settings()
