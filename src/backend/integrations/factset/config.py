"""
FactSet Integration Configuration

This module provides configuration management for FactSet integrations
including environment variables, default settings, and validation.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FactSetConfig:
    """FactSet SDK configuration"""
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    base_url: str = "https://api.factset.com"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class GoDrillConfig:
    """Go-Drill configuration"""
    connection_string: str = "localhost:8047"
    use_tls: bool = False
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 30
    max_connections: int = 10


@dataclass
class QuartOpenAPIConfig:
    """Quart-OpenAPI configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None
    rate_limit: Optional[int] = None
    api_version: str = "v1"


@dataclass
class AnalyticsEnginesConfig:
    """Analytics Engines configuration"""
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    base_url: str = "https://api.factset.com/analytics"
    timeout: int = 60
    max_concurrent_jobs: int = 5


@dataclass
class STACHConfig:
    """STACH Schema configuration"""
    schema_version: str = "1.0"
    default_currency: str = "USD"
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%dT%H:%M:%S"
    decimal_places: int = 4


@dataclass
class FinancialIntelligenceConfig:
    """Financial Intelligence Layer configuration"""
    cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 10000
    enable_caching: bool = True
    fallback_sources: list = None
    rate_limit_per_minute: int = 1000


class FactSetIntegrationConfig:
    """Main configuration class for all FactSet integrations"""
    
    def __init__(self):
        self.factset = self._load_factset_config()
        self.go_drill = self._load_go_drill_config()
        self.quart_openapi = self._load_quart_openapi_config()
        self.analytics_engines = self._load_analytics_engines_config()
        self.stach = self._load_stach_config()
        self.financial_intelligence = self._load_financial_intelligence_config()
        
        # Validate configuration
        self._validate_config()
    
    def _load_factset_config(self) -> FactSetConfig:
        """Load FactSet SDK configuration"""
        return FactSetConfig(
            username=os.getenv('FACTSET_USERNAME'),
            password=os.getenv('FACTSET_PASSWORD'),
            api_key=os.getenv('FACTSET_API_KEY'),
            base_url=os.getenv('FACTSET_BASE_URL', 'https://api.factset.com'),
            timeout=int(os.getenv('FACTSET_TIMEOUT', '30')),
            retry_attempts=int(os.getenv('FACTSET_RETRY_ATTEMPTS', '3')),
            retry_delay=float(os.getenv('FACTSET_RETRY_DELAY', '1.0'))
        )
    
    def _load_go_drill_config(self) -> GoDrillConfig:
        """Load Go-Drill configuration"""
        return GoDrillConfig(
            connection_string=os.getenv('GO_DRILL_CONNECTION_STRING', 'localhost:8047'),
            use_tls=os.getenv('GO_DRILL_USE_TLS', 'false').lower() == 'true',
            username=os.getenv('GO_DRILL_USERNAME'),
            password=os.getenv('GO_DRILL_PASSWORD'),
            timeout=int(os.getenv('GO_DRILL_TIMEOUT', '30')),
            max_connections=int(os.getenv('GO_DRILL_MAX_CONNECTIONS', '10'))
        )
    
    def _load_quart_openapi_config(self) -> QuartOpenAPIConfig:
        """Load Quart-OpenAPI configuration"""
        cors_origins = os.getenv('QUART_CORS_ORIGINS', '*').split(',')
        
        return QuartOpenAPIConfig(
            host=os.getenv('QUART_HOST', '0.0.0.0'),
            port=int(os.getenv('QUART_PORT', '8000')),
            debug=os.getenv('QUART_DEBUG', 'false').lower() == 'true',
            cors_origins=cors_origins,
            rate_limit=int(os.getenv('QUART_RATE_LIMIT')) if os.getenv('QUART_RATE_LIMIT') else None,
            api_version=os.getenv('QUART_API_VERSION', 'v1')
        )
    
    def _load_analytics_engines_config(self) -> AnalyticsEnginesConfig:
        """Load Analytics Engines configuration"""
        return AnalyticsEnginesConfig(
            username=os.getenv('ANALYTICS_USERNAME'),
            password=os.getenv('ANALYTICS_PASSWORD'),
            api_key=os.getenv('ANALYTICS_API_KEY'),
            base_url=os.getenv('ANALYTICS_BASE_URL', 'https://api.factset.com/analytics'),
            timeout=int(os.getenv('ANALYTICS_TIMEOUT', '60')),
            max_concurrent_jobs=int(os.getenv('ANALYTICS_MAX_CONCURRENT_JOBS', '5'))
        )
    
    def _load_stach_config(self) -> STACHConfig:
        """Load STACH Schema configuration"""
        return STACHConfig(
            schema_version=os.getenv('STACH_SCHEMA_VERSION', '1.0'),
            default_currency=os.getenv('STACH_DEFAULT_CURRENCY', 'USD'),
            date_format=os.getenv('STACH_DATE_FORMAT', '%Y-%m-%d'),
            datetime_format=os.getenv('STACH_DATETIME_FORMAT', '%Y-%m-%dT%H:%M:%S'),
            decimal_places=int(os.getenv('STACH_DECIMAL_PLACES', '4'))
        )
    
    def _load_financial_intelligence_config(self) -> FinancialIntelligenceConfig:
        """Load Financial Intelligence Layer configuration"""
        fallback_sources = os.getenv('FINANCIAL_INTELLIGENCE_FALLBACK_SOURCES', 'polygon,yahoo,coingecko').split(',')
        
        return FinancialIntelligenceConfig(
            cache_ttl=int(os.getenv('FINANCIAL_INTELLIGENCE_CACHE_TTL', '300')),
            max_cache_size=int(os.getenv('FINANCIAL_INTELLIGENCE_MAX_CACHE_SIZE', '10000')),
            enable_caching=os.getenv('FINANCIAL_INTELLIGENCE_ENABLE_CACHING', 'true').lower() == 'true',
            fallback_sources=fallback_sources,
            rate_limit_per_minute=int(os.getenv('FINANCIAL_INTELLIGENCE_RATE_LIMIT_PER_MINUTE', '1000'))
        )
    
    def _validate_config(self):
        """Validate configuration settings"""
        warnings = []
        errors = []
        
        # Validate FactSet configuration
        if not self.factset.username:
            warnings.append("FACTSET_USERNAME not set")
        if not self.factset.password:
            warnings.append("FACTSET_PASSWORD not set")
        if not self.factset.api_key:
            warnings.append("FACTSET_API_KEY not set")
        
        # Validate Go-Drill configuration
        if not self.go_drill.connection_string:
            errors.append("GO_DRILL_CONNECTION_STRING not set")
        
        # Validate Analytics Engines configuration
        if not self.analytics_engines.username:
            warnings.append("ANALYTICS_USERNAME not set")
        if not self.analytics_engines.password:
            warnings.append("ANALYTICS_PASSWORD not set")
        if not self.analytics_engines.api_key:
            warnings.append("ANALYTICS_API_KEY not set")
        
        # Log warnings and errors
        if warnings:
            logger.warning("Configuration warnings:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
        
        if errors:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'factset': {
                'username': self.factset.username,
                'password': self.factset.password,
                'api_key': self.factset.api_key,
                'base_url': self.factset.base_url,
                'timeout': self.factset.timeout,
                'retry_attempts': self.factset.retry_attempts,
                'retry_delay': self.factset.retry_delay
            },
            'go_drill': {
                'connection_string': self.go_drill.connection_string,
                'use_tls': self.go_drill.use_tls,
                'username': self.go_drill.username,
                'password': self.go_drill.password,
                'timeout': self.go_drill.timeout,
                'max_connections': self.go_drill.max_connections
            },
            'quart_openapi': {
                'host': self.quart_openapi.host,
                'port': self.quart_openapi.port,
                'debug': self.quart_openapi.debug,
                'cors_origins': self.quart_openapi.cors_origins,
                'rate_limit': self.quart_openapi.rate_limit,
                'api_version': self.quart_openapi.api_version
            },
            'analytics_engines': {
                'username': self.analytics_engines.username,
                'password': self.analytics_engines.password,
                'api_key': self.analytics_engines.api_key,
                'base_url': self.analytics_engines.base_url,
                'timeout': self.analytics_engines.timeout,
                'max_concurrent_jobs': self.analytics_engines.max_concurrent_jobs
            },
            'stach': {
                'schema_version': self.stach.schema_version,
                'default_currency': self.stach.default_currency,
                'date_format': self.stach.date_format,
                'datetime_format': self.stach.datetime_format,
                'decimal_places': self.stach.decimal_places
            },
            'financial_intelligence': {
                'cache_ttl': self.financial_intelligence.cache_ttl,
                'max_cache_size': self.financial_intelligence.max_cache_size,
                'enable_caching': self.financial_intelligence.enable_caching,
                'fallback_sources': self.financial_intelligence.fallback_sources,
                'rate_limit_per_minute': self.financial_intelligence.rate_limit_per_minute
            }
        }
    
    def get_env_template(self) -> str:
        """Generate .env template file"""
        return """# FactSet Integration Configuration
# Copy this to your .env file and fill in your credentials

# FactSet SDK Configuration
FACTSET_USERNAME=your_factset_username
FACTSET_PASSWORD=your_factset_password
FACTSET_API_KEY=your_factset_api_key
FACTSET_BASE_URL=https://api.factset.com
FACTSET_TIMEOUT=30
FACTSET_RETRY_ATTEMPTS=3
FACTSET_RETRY_DELAY=1.0

# Go-Drill Configuration
GO_DRILL_CONNECTION_STRING=localhost:8047
GO_DRILL_USE_TLS=false
GO_DRILL_USERNAME=your_drill_username
GO_DRILL_PASSWORD=your_drill_password
GO_DRILL_TIMEOUT=30
GO_DRILL_MAX_CONNECTIONS=10

# Quart-OpenAPI Configuration
QUART_HOST=0.0.0.0
QUART_PORT=8000
QUART_DEBUG=false
QUART_CORS_ORIGINS=*
QUART_RATE_LIMIT=1000
QUART_API_VERSION=v1

# Analytics Engines Configuration
ANALYTICS_USERNAME=your_analytics_username
ANALYTICS_PASSWORD=your_analytics_password
ANALYTICS_API_KEY=your_analytics_api_key
ANALYTICS_BASE_URL=https://api.factset.com/analytics
ANALYTICS_TIMEOUT=60
ANALYTICS_MAX_CONCURRENT_JOBS=5

# STACH Schema Configuration
STACH_SCHEMA_VERSION=1.0
STACH_DEFAULT_CURRENCY=USD
STACH_DATE_FORMAT=%Y-%m-%d
STACH_DATETIME_FORMAT=%Y-%m-%dT%H:%M:%S
STACH_DECIMAL_PLACES=4

# Financial Intelligence Layer Configuration
FINANCIAL_INTELLIGENCE_CACHE_TTL=300
FINANCIAL_INTELLIGENCE_MAX_CACHE_SIZE=10000
FINANCIAL_INTELLIGENCE_ENABLE_CACHING=true
FINANCIAL_INTELLIGENCE_FALLBACK_SOURCES=polygon,yahoo,coingecko
FINANCIAL_INTELLIGENCE_RATE_LIMIT_PER_MINUTE=1000
"""


# Global configuration instance
_config = None

def get_config() -> FactSetIntegrationConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = FactSetIntegrationConfig()
    return _config


def reload_config():
    """Reload configuration from environment"""
    global _config
    _config = FactSetIntegrationConfig()
    logger.info("Configuration reloaded")


def validate_credentials() -> bool:
    """Validate that required credentials are set"""
    config = get_config()
    
    # Check critical credentials
    critical_credentials = [
        (config.factset.username, "FACTSET_USERNAME"),
        (config.factset.password, "FACTSET_PASSWORD"),
        (config.factset.api_key, "FACTSET_API_KEY")
    ]
    
    missing = [name for value, name in critical_credentials if not value]
    
    if missing:
        logger.error(f"Missing critical credentials: {', '.join(missing)}")
        return False
    
    return True


def get_connection_status() -> Dict[str, bool]:
    """Get connection status for all integrations"""
    config = get_config()
    
    status = {
        'factset': bool(config.factset.username and config.factset.password and config.factset.api_key),
        'go_drill': bool(config.go_drill.connection_string),
        'analytics_engines': bool(config.analytics_engines.username and config.analytics_engines.password and config.analytics_engines.api_key),
        'quart_openapi': True,  # Always available
        'stach': True,  # Always available
        'financial_intelligence': True  # Always available
    }
    
    return status


if __name__ == "__main__":
    # Generate .env template
    config = FactSetIntegrationConfig()
    print(config.get_env_template())
    
    # Validate configuration
    if validate_credentials():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors")
    
    # Show connection status
    status = get_connection_status()
    print("\nConnection Status:")
    for service, connected in status.items():
        status_icon = "✅" if connected else "❌"
        print(f"  {status_icon} {service}: {'Connected' if connected else 'Not Configured'}")
