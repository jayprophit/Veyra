"""
Application Configuration
Loads settings from environment variables with sensible defaults
"""
from typing import List
from functools import lru_cache
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # ========== Application ==========
    APP_NAME: str = "Veyra"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ========== Server ==========
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # ========== CORS & Security ==========
    ALLOWED_HOSTS: str = "*"  # Parse as string first
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000"

    # ========== Database ==========
    DATABASE_URL: str = "sqlite+aiosqlite:///./veyra.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # ========== Authentication ==========
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ========== External APIs ==========
    POLYGON_API_KEY: str = ""
    ALPACA_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    COINMARKETCAP_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""
    FMP_API_KEY: str = ""
    EODHD_API_TOKEN: str = ""

    # ========== Feature Flags ==========
    ENABLE_TRADING: bool = True
    ENABLE_AI_ANALYSIS: bool = True
    ENABLE_PAPER_TRADING: bool = True
    ENABLE_MOCK_DATA: bool = True

    # ========== Logging ==========
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/veyra.log"
    LOG_FORMAT: str = "json"

    # ========== Sentry ==========
    SENTRY_DSN: str = ""
    SENTRY_ENABLED: bool = False

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v if isinstance(v, list) else ["*"]

    @field_validator("ALLOWED_HOSTS", mode="after")
    @classmethod
    def parse_allowed_hosts(cls, v):
        """Parse ALLOWED_HOSTS from comma-separated string"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v if isinstance(v, list) else ["*"]


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (cached)"""
    return Settings()


# Create global settings instance
settings = get_settings()
