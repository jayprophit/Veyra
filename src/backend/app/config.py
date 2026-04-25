"""
Configuration - Live Data First
=================================
All configuration settings. Real data is default.
"""

import os
from typing import Optional


class Config:
    """Application configuration."""
    
    # Data Source Priority
    # Options: 'live', 'cached', 'mock'
    # Default is 'live' - will use real APIs
    DATA_SOURCE = os.getenv('DATA_SOURCE', 'live')
    
    # API Keys (from environment)
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
    
    # Alpaca Settings
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    ALPACA_PAPER_TRADING = os.getenv('ALPACA_PAPER_TRADING', 'true').lower() == 'true'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///financial_master.db')
    
    # Cache Settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL', '30'))
    
    # WebSocket
    WS_ENABLED = os.getenv('WS_ENABLED', 'true').lower() == 'true'
    WS_REFRESH_INTERVAL = int(os.getenv('WS_REFRESH_INTERVAL', '5'))
    
    # Feature Flags
    ENABLE_REALTIME_PRICES = os.getenv('ENABLE_REALTIME_PRICES', 'true').lower() == 'true'
    ENABLE_LIVE_TRADING = os.getenv('ENABLE_LIVE_TRADING', 'false').lower() == 'true'
    ENABLE_AUTO_REFRESH = os.getenv('ENABLE_AUTO_REFRESH', 'true').lower() == 'true'
    
    @classmethod
    def is_live_data_configured(cls) -> bool:
        """Check if any live data source is configured."""
        return any([
            cls.POLYGON_API_KEY,
            cls.ALPACA_API_KEY,
            cls.ALPHA_VANTAGE_KEY
        ])
    
    @classmethod
    def get_data_source_priority(cls) -> list:
        """Get priority list of data sources."""
        if cls.DATA_SOURCE == 'live':
            return ['polygon', 'alpaca', 'yahoo', 'alpha_vantage', 'mock']
        elif cls.DATA_SOURCE == 'cached':
            return ['cached', 'polygon', 'alpaca', 'mock']
        else:
            return ['mock']
    
    @classmethod
    def validate(cls) -> dict:
        """Validate configuration and return status."""
        issues = []
        warnings = []
        
        # Check API keys
        if not cls.POLYGON_API_KEY:
            warnings.append("POLYGON_API_KEY not set - using fallback sources")
        
        if not cls.ALPACA_API_KEY:
            warnings.append("ALPACA_API_KEY not set - live trading disabled")
        
        if not cls.ALPHA_VANTAGE_KEY:
            warnings.append("ALPHA_VANTAGE_KEY not set - free tier alternative unavailable")
        
        # Check data source
        if cls.DATA_SOURCE == 'live' and not cls.is_live_data_configured():
            issues.append("DATA_SOURCE=live but no API keys configured")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'data_source': cls.DATA_SOURCE,
            'live_configured': cls.is_live_data_configured()
        }


# Global config instance
config = Config()
