"""
Configuration Management
=========================
Centralized configuration from environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    db_type: str = "sqlite"
    db_url: Optional[str] = None
    sqlite_path: str = "./data/veyra.db"
    pool_size: int = 10
    max_overflow: int = 20
    echo_sql: bool = False
    
    class Config:
        env_prefix = "DB_"


class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    class Config:
        env_prefix = "SEC_"


class APISettings(BaseSettings):
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 4
    log_level: str = "INFO"
    cors_origins: list = ["*"]
    title: str = "Veyra API"
    version: str = "1.0.0"
    
    class Config:
        env_prefix = "API_"


class BrokerSettings(BaseSettings):
    """Broker API configuration"""
    # Alpaca
    alpaca_api_key: Optional[str] = None
    alpaca_secret_key: Optional[str] = None
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    
    # Polygon
    polygon_api_key: Optional[str] = None
    polygon_base_url: str = "https://api.polygon.io"
    
    # MetaTrader 5
    metatrader_server: Optional[str] = None
    metatrader_login: Optional[str] = None
    metatrader_password: Optional[str] = None
    
    use_paper_trading: bool = True
    
    class Config:
        env_prefix = "BROKER_"


class AIMLSettings(BaseSettings):
    """AI/ML configuration"""
    llm_provider: str = "ollama"  # ollama, openai, anthropic
    ollama_model: str = "llama3.2:3b"
    ollama_base_url: str = "http://localhost:11434"
    
    # Optional paid LLM
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Model settings
    model_temperature: float = 0.7
    model_max_tokens: int = 2000
    enable_caching: bool = True
    
    # Agent settings
    max_daily_trades: int = 5
    max_daily_value: float = 100000
    max_single_trade: float = 25000
    require_approval_above: float = 10000
    
    class Config:
        env_prefix = "AIML_"


class NotificationSettings(BaseSettings):
    """Notification configuration"""
    # Email
    enable_email: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    email_sender: Optional[str] = None
    
    # Telegram
    enable_telegram: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # SMS
    enable_sms: bool = False
    sms_provider: Optional[str] = None  # twilio, etc
    sms_api_key: Optional[str] = None
    
    class Config:
        env_prefix = "NOTIFY_"


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration"""
    log_level: str = "INFO"
    enable_prometheus: bool = False
    prometheus_port: int = 8001
    enable_sentry: bool = False
    sentry_dsn: Optional[str] = None
    enable_performance_tracking: bool = True
    
    class Config:
        env_prefix = "MONITOR_"


class Settings(BaseSettings):
    """Main application settings"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    api: APISettings = APISettings()
    broker: BrokerSettings = BrokerSettings()
    aiml: AIMLSettings = AIMLSettings()
    notification: NotificationSettings = NotificationSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


def get_db_url() -> str:
    """Get database URL"""
    if settings.database.db_url:
        return settings.database.db_url
    
    if settings.database.db_type == "sqlite":
        return f"sqlite:///{settings.database.sqlite_path}"
    elif settings.database.db_type == "postgresql":
        return f"postgresql://{settings.database.db_url}"
    elif settings.database.db_type == "mysql":
        return f"mysql+pymysql://{settings.database.db_url}"
    else:
        raise ValueError(f"Unsupported database type: {settings.database.db_type}")


def is_production() -> bool:
    """Check if running in production"""
    return settings.environment == Environment.PRODUCTION


def is_development() -> bool:
    """Check if running in development"""
    return settings.environment == Environment.DEVELOPMENT


def is_testing() -> bool:
    """Check if running in testing"""
    return settings.environment == Environment.TESTING
