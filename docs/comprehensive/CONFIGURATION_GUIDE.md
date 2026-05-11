# Comprehensive Configuration Guide
## 100% Open-Source Veyra Configuration

## Overview

This guide provides complete configuration instructions for **100% open-source** Veyra. No API keys required, all data sources are free and open.

## Environment Configuration

### Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# Open-Source Data Sources (NO API KEYS REQUIRED)
OPENSOURCE_ENABLED=true
OPENSOURCE_CACHE_TTL=300
OPENSOURCE_RATE_LIMIT_ENABLED=true

# Primary Data Sources Configuration
YFINANCE_ENABLED=true
YFINANCE_RATE_LIMIT=2000
PANDAS_DATAREADER_ENABLED=true
PANDAS_DATAREADER_RATE_LIMIT=1000
INVESTPY_ENABLED=true
INVESTPY_RATE_LIMIT=100

# Secondary Data Sources Configuration
FRED_ENABLED=true
FRED_RATE_LIMIT=120
WORLD_BANK_ENABLED=true
WORLD_BANK_RATE_LIMIT=100
ALPHA_VANTAGE_ENABLED=false
ALPHA_VANTAGE_RATE_LIMIT=5

# Fallback Data Sources Configuration
CRYPTOCOMPARE_ENABLED=true
CRYPTOCOMPARE_RATE_LIMIT=100
POLYGON_ENABLED=false
POLYGON_RATE_LIMIT=5
IEX_CLOUD_ENABLED=false
IEX_CLOUD_RATE_LIMIT=100

# AI/ML Configuration
HUGGINGFACE_ENABLED=true
HUGGINGFACE_CACHE_MODELS=true
SCIKIT_LEARN_ENABLED=true
TENSORFLOW_ENABLED=true

# GitHub Integration
GITHUB_ENABLED=true
GITHUB_CACHE_REPOSITORIES=true

# Kaggle Integration
KAGGLE_ENABLED=true
KAGGLE_CACHE_DATASETS=true

# Database Configuration
DATABASE_URL=sqlite:///./veyra.db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=300

# Application Configuration
APP_NAME=Veyra
APP_VERSION=2.0.0
APP_DEBUG=false
APP_LOG_LEVEL=INFO

# Security Configuration
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
CORS_ORIGINS=*

# Performance Configuration
CACHE_ENABLED=true
CACHE_TTL=300
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000

# OPTIONAL PAID DEPENDENCIES (COMMENTED OUT - UNLOCK IF NEEDED)
# ================================================================
# Alpha Vantage (Optional - Free Tier Available)
# ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
# ALPHA_VANTAGE_RATE_LIMIT=5
# ALPHA_VANTAGE_TIMEOUT=30

# Polygon.io (Optional - Free Tier Available)
# POLYGON_API_KEY=your_polygon_key
# POLYGON_RATE_LIMIT=5

# Quandl (Optional - Free Tier Available)
# QUANDL_API_KEY=your_quandl_key
# QUANDL_RATE_LIMIT=50

# NOTE: All core functionality works without these optional keys
# Only enable if you need higher rate limits or premium features

# Open-Source Technical Analysis
TECHNICAL_ANALYSIS_LIBRARY=talib
TECHNICAL_INDICATORS=sma,ema,rsi,macd,bollinger

# Open-Source Machine Learning
ML_FRAMEWORK=scikit-learn
ML_MODEL_CACHE=true

# Open-Source Data Processing
DATA_PROCESSING_BACKEND=pandas
DATA_CACHE_ENABLED=true

# Open-Source Machine Learning
ML_ENABLED=true
ML_MODELS=random_forest,linear_regression,xgboost
ML_FRAMEWORK=scikit-learn

# Open-Source Data Cache
ENHANCED_DATA_CACHE_TTL=300
ENHANCED_DATA_MAX_POINTS=10000
ENHANCED_DATA_ENABLE_MOCK=false

# FREE ALTERNATIVES TO FACTSET (100% Open-Source)
OPENBB_ENABLED=true
OPENBB_CACHE_ENABLED=true
YFINANCE_ENABLED=true
YFINANCE_CACHE_ENABLED=true
EDGAR_ENABLED=true
FINANCE_TOOLKIT_ENABLED=true
OPENBB_CACHE_TTL=300
OPENBB_RATE_LIMIT=none

YFINANCE_ENABLED=true
YFINANCE_CACHE_TTL=300
YFINANCE_RATE_LIMIT=none

EDGAR_ENABLED=true
EDGAR_CACHE_TTL=1800
EDGAR_RATE_LIMIT=10

FINANCETOOLKIT_ENABLED=true
FINANCETOOLKIT_CACHE_TTL=600
FINANCETOOLKIT_RATE_LIMIT=none

# Free Data Sources Configuration
FREE_DATA_SOURCES_ENABLED=true
FREE_DATA_PRIMARY_SOURCE=openbb
FREE_DATA_FALLBACK_SOURCES=yfinance,edgar,finance_toolkit
FREE_DATA_USE_MOCK_FALLBACK=true

# Data Source Priority
MARKET_DATA_PRIORITY=openbb,yfinance
FUNDAMENTALS_PRIORITY=openbb,yfinance
SEC_FILINGS_PRIORITY=edgar
ANALYSIS_PRIORITY=finance_toolkit,openbb

# Go-Drill Integration
GO_DRILL_CONNECTION_STRING=localhost:8047
GO_DRILL_USE_TLS=false
GO_DRILL_USERNAME=your_drill_username
GO_DRILL_PASSWORD=your_drill_password
GO_DRILL_TIMEOUT=30
GO_DRILL_MAX_CONNECTIONS=10

# STACH Schema Integration
STACH_SCHEMA_VERSION=1.0
STACH_DEFAULT_CURRENCY=USD
STACH_DATE_FORMAT=%Y-%m-%d
STACH_DATETIME_FORMAT=%Y-%m-%dT%H:%M:%S
STACH_DECIMAL_PLACES=4

# Financial Intelligence Layer
FINANCIAL_INTELLIGENCE_CACHE_TTL=300
FINANCIAL_INTELLIGENCE_MAX_CACHE_SIZE=10000
FINANCIAL_INTELLIGENCE_ENABLE_CACHING=true
FINANCIAL_INTELLIGENCE_RATE_LIMIT_PER_MINUTE=1000

# Analytics Engines
ANALYTICS_USERNAME=your_factset_username
ANALYTICS_PASSWORD=your_factset_password
ANALYTICS_API_KEY=your_factset_api_key
ANALYTICS_BASE_URL=https://api.factset.com/analytics
ANALYTICS_TIMEOUT=60
ANALYTICS_MAX_CONCURRENT_JOBS=5

# Quart-OpenAPI
QUART_HOST=0.0.0.0
QUART_PORT=8000
QUART_DEBUG=false
QUART_CORS_ORIGINS=*
QUART_RATE_LIMIT=1000
QUART_API_VERSION=v1
```

## Configuration Files

### Main Configuration

Create `config/config.py` for production settings:

```python
# config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # FactSet Configuration
    FACTSET_USERNAME = os.getenv('FACTSET_USERNAME')
    FACTSET_PASSWORD = os.getenv('FACTSET_PASSWORD')
    FACTSET_API_KEY = os.getenv('FACTSET_API_KEY')
    FACTSET_BASE_URL = os.getenv('FACTSET_BASE_URL', 'https://api.factset.com')
    
    # Enhanced Repositories
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
    QUANTCONNECT_API_KEY = os.getenv('QUANTCONNECT_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/veyra')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '30'))
    
    # Performance
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    
    @staticmethod
    def validate():
        """Validate configuration"""
        required_vars = [
            'FACTSET_USERNAME',
            'FACTSET_PASSWORD',
            'FACTSET_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(Config, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return True
```

### Development Configuration

Create `config/development.py` for development settings:

```python
# config/development.py
import os
from .config import Config

class DevelopmentConfig(Config):
    # Override for development
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Development databases
    DATABASE_URL = os.getenv('DEV_DATABASE_URL', 'sqlite:///dev.db')
    
    # Mock external APIs
    ENABLE_MOCK_APIS = os.getenv('ENABLE_MOCK_APIS', 'true').lower() == 'true'
    
    # Development tools
    ENABLE_PROFILING = os.getenv('ENABLE_PROFILING', 'false').lower() == 'true'
    ENABLE_DEBUG_TOOLBAR = os.getenv('ENABLE_DEBUG_TOOLBAR', 'true').lower() == 'true'
```

### Production Configuration

Create `config/production.py` for production settings:

```python
# config/production.py
import os
from .config import Config

class ProductionConfig(Config):
    # Production settings
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # Production databases
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')
    
    # Production security
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Performance optimizations
    ENABLE_CACHING = True
    CACHE_TTL = 300
    MAX_WORKERS = 8
    
    # Monitoring
    ENABLE_METRICS = True
    METRICS_PORT = 9090
```

## Database Configuration

### PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE veyra;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Portfolio table
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Holdings table
CREATE TABLE holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    symbol VARCHAR(10) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    purchase_price DECIMAL(20, 8),
    current_price DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market data cache
CREATE TABLE market_data_cache (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(20) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    UNIQUE(symbol, timestamp, source)
);

-- Technical indicators cache
CREATE TABLE technical_indicators (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    value DECIMAL(20, 8) NOT NULL,
    signal VARCHAR(10),
    confidence DECIMAL(5, 4),
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(20) NOT NULL,
    UNIQUE(symbol, indicator_name, timestamp)
);
```

### Redis Configuration

```python
# Redis configuration for caching
import redis
import json
from datetime import timedelta

class RedisCache:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 300  # 5 minutes
    
    async def get(self, key):
        """Get cached value"""
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key, value, ttl=None):
        """Set cached value"""
        ttl = ttl or self.default_ttl
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key):
        """Delete cached value"""
        await self.redis.delete(key)
    
    async def clear_pattern(self, pattern):
        """Clear cache by pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

## API Configuration

### Rate Limiting

```python
# Rate limiting configuration
from slowapi import HTTPException
from slowapi.middleware import RateLimiter
from slowapi import status

# Rate limiter middleware
rate_limiter = RateLimiter(
    calls=100,  # 100 requests per minute
    period=60
)

@rate_limiter
async def rate_limited_endpoint():
    """Rate limited endpoint example"""
    return {"message": "Rate limited endpoint"}

# Custom rate limiting
class CustomRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.limits = {
            'free_tier': {'requests': 100, 'window': 60},
            'premium_tier': {'requests': 1000, 'window': 60}
        }
    
    async def is_allowed(self, user_tier, endpoint):
        """Check if user is allowed to make request"""
        key = f"rate_limit:{user_tier}:{endpoint}"
        current = await self.redis.get(key)
        
        if current:
            current_data = json.loads(current)
            return current_data['count'] < self.limits[user_tier]['requests']
        
        return True  # Allow if no record found
```

### Security Configuration

```python
# Security configuration
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import secrets

class SecurityConfig:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY')
        self.jwt_algorithm = 'HS256'
        self.jwt_expiration = timedelta(minutes=30)
        
        # Initialize encryption
        self.cipher_suite = Fernet(self.secret_key.encode())
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def generate_api_key(self):
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password):
        """Hash password securely"""
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)
```

## Monitoring Configuration

### Logging Setup

```python
# Logging configuration
import logging
import structlog
from pythonjsonlogger import jsonlogger

# Structured logging
def setup_logging():
    """Setup comprehensive logging"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ],
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    
    # Configure JSON logger
    logger = structlog.get_logger()
    json_logger = jsonlogger(logger)
    
    return json_logger

# Performance monitoring
import psutil
import time

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}
    
    def track_request(self, endpoint, duration):
        """Track API request performance"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        
        self.metrics[endpoint].append(duration)
        
        # Alert on slow requests
        if duration > 1.0:  # 1 second threshold
            logger.warning(f"Slow request: {endpoint} took {duration:.3f}s")
    
    def get_metrics(self):
        """Get performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/'),
            'request_metrics': self.metrics
        }
```

## Testing Configuration

### Test Environment

```python
# Test configuration
import pytest
import asyncio
from unittest.mock import Mock, patch

class TestConfig:
    # Test database
    DATABASE_URL = 'sqlite:///test.db'
    
    # Mock external APIs
    ENABLE_MOCK_APIS = True
    
    # Test fixtures
    API_KEYS = {
        'factset': 'test_factset_key',
        'alpha_vantage': 'test_alpha_vantage_key',
        'polygon': 'test_polygon_key'
    }
    
    # Test data
    SAMPLE_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']
    SAMPLE_DATES = {
        'start': '2024-01-01',
        'end': '2024-12-31'
    }

# Mock fixtures
@pytest.fixture
def mock_factset_client():
    """Mock FactSet client for testing"""
    with patch('factset.enterprise_sdk.FactSetClient') as mock_client:
        mock_client.return_value = Mock(
            get_portfolio_analytics=Mock(return_value={'total_return': 0.15}),
            get_market_data=Mock(return_value=[])
        )
        yield mock_client

# Integration tests
@pytest.mark.asyncio
async def test_factset_integration():
    """Test FactSet integration"""
    from src.backend.integrations.factset.financial_intelligence_layer import get_financial_intelligence_layer
    
    config = TestConfig()
    financial_intelligence = get_financial_intelligence_layer(config)
    
    # Test real-time data
    quotes = await financial_intelligence.get_real_time_quotes(['AAPL'])
    assert len(quotes) > 0
    assert quotes[0]['symbol'] == 'AAPL'
    
    # Test technical indicators
    risk_metrics = await financial_intelligence.get_advanced_risk_metrics(['AAPL'])
    assert 'beta' in risk_metrics['AAPL']
```

## Deployment Configuration

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Configuration

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: veyra
spec:
  replicas: 3
  selector:
    matchLabels:
      app: veyra
  template:
    metadata:
      labels:
        app: veyra
    spec:
      containers:
      - name: veyra
        image: veyra:latest
        ports:
        - containerPort: 8000
        env:
          - name: DATABASE_URL
            valueFrom:
              secretKeyRef:
                name: veyra-secrets
                key: database-url
          - name: SECRET_KEY
            valueFrom:
              secretKeyRef:
                name: veyra-secrets
                key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: veyra-service
spec:
  selector:
    app: veyra
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: veyra-secrets
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  secret-key: <base64-encoded-secret-key>
```

### Environment-Specific Configurations

#### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - DATABASE_URL=sqlite:///dev.db
      - ENABLE_MOCK_APIS=true
    volumes:
      - ./src:/app
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=financial_master_dev
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=dev
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

#### Production Environment
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: veyra:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## Validation

### Configuration Validation

```python
# Configuration validation
import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigValidator:
    def __init__(self):
        self.required_vars = {
            'factset': ['FACTSET_USERNAME', 'FACTSET_PASSWORD', 'FACTSET_API_KEY'],
            'enhanced': ['ALPHA_VANTAGE_API_KEY', 'POLYGON_API_KEY'],
            'database': ['DATABASE_URL'],
            'security': ['SECRET_KEY']
        }
    
    def validate_all(self) -> ValidationResult:
        """Validate all configuration"""
        errors = []
        warnings = []
        
        for category, vars_list in self.required_vars.items():
            missing_vars = []
            for var in vars_list:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                errors.append(f"Missing {category} variables: {', '.join(missing_vars)}")
            
            # Check optional configurations
            if category == 'database':
                db_url = os.getenv('DATABASE_URL')
                if db_url and not db_url.startswith(('postgresql://', 'mysql://')):
                    warnings.append("Database URL should use PostgreSQL or MySQL")
            
            elif category == 'security':
                secret_key = os.getenv('SECRET_KEY')
                if secret_key and len(secret_key) < 32:
                    warnings.append("SECRET_KEY should be at least 32 characters")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_api_keys(self) -> ValidationResult:
        """Validate API key formats"""
        errors = []
        warnings = []
        
        api_keys = {
            'FACTSET_API_KEY': os.getenv('FACTSET_API_KEY'),
            'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'POLYGON_API_KEY': os.getenv('POLYGON_API_KEY')
        }
        
        for key_name, key_value in api_keys.items():
            if key_value:
                # Check FactSet key format (should be 32 characters)
                if key_name.startswith('FACTSET_') and len(key_value) != 32:
                    errors.append(f"{key_name} should be 32 characters")
                
                # Check Alpha Vantage key format
                elif key_name.startswith('ALPHA_VANTAGE_') and not key_value.isalnum():
                    warnings.append(f"{key_name} contains non-alphanumeric characters")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

## Troubleshooting

### Common Issues

#### 1. API Connection Issues

**Problem**: Cannot connect to FactSet APIs
**Solutions**:
- Verify API credentials in environment variables
- Check network connectivity to FactSet endpoints
- Validate API key format and permissions
- Check rate limiting status
- Review API service status page

#### 2. Database Issues

**Problem**: Database connection failed
**Solutions**:
- Verify DATABASE_URL format
- Check database server is running
- Validate database credentials
- Check firewall settings
- Review database logs

#### 3. Performance Issues

**Problem**: Slow API response times
**Solutions**:
- Enable Redis caching
- Optimize database queries
- Implement connection pooling
- Use async operations
- Monitor performance metrics

#### 4. Memory Issues

**Problem**: High memory usage
**Solutions**:
- Implement data streaming for large datasets
- Use generators instead of lists
- Optimize data structures
- Monitor memory usage
- Implement garbage collection

### Debug Mode

Enable debug mode for development:

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Enable mock APIs
export ENABLE_MOCK_APIS=true

# Enable profiling
export ENABLE_PROFILING=true
```

---

**Last Updated:** May 2026  
**Version:** 2.0.0  
**License:** MIT
