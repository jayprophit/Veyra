# Development Setup Guide
## 100% Open-Source Veyra Development

## Overview

This guide provides comprehensive setup instructions for developing **100% open-source** Veyra. No API keys required, all dependencies are free and open-source.

## Prerequisites

### System Requirements

- **Python 3.11+** (3.12+ recommended)
- **Node.js 18+** (for frontend development)
- **Git** (for version control)
- **Docker** (optional, for containerized development)
- **VS Code** (recommended IDE)
- **PostgreSQL 15+** (optional, for production database)
- **Redis 6+** (optional, for caching and session management)

### Development Tools

#### Recommended IDE Extensions
- **Python**: Python, Pylance, Python Docstring Generator
- **VS Code**: Python, Pylance, Docker, Remote Development
- **Database**: PostgreSQL, Redis Explorer
- **Git**: GitLens, Git Graph
- **Testing**: Python Test Explorer, Coverage Gutters

## Quick Start

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/jpowell/veyra.git
cd veyra

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install open-source dependencies
pip install -r requirements_opensource.txt
```

### 2. Environment Configuration

#### Create Environment File

```bash
# Copy environment template
cp .env.example .env

# No API keys required for open-source version!
# All data sources are free and open
# See: docs/opensource/OPENSOURCE_GUIDE.md
nano .env
```

#### Environment Variables

```bash
# Core Configuration (Open-Source)
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Open-Source Data Sources (NO API KEYS REQUIRED)
OPENSOURCE_ENABLED=true
YFINANCE_ENABLED=true
PANDAS_DATAREADER_ENABLED=true
FRED_ENABLED=true
HUGGINGFACE_ENABLED=true

# Database Configuration
DATABASE_URL=postgresql://localhost:5432/veyra
REDIS_URL=redis://localhost:6379/0

# OPTIONAL PAID DEPENDENCIES (COMMENTED OUT - UNLOCK IF NEEDED)
# ================================================================
# FactSet Configuration (Optional - Paid)
# FACTSET_USERNAME=your_factset_username
# FACTSET_PASSWORD=your_factset_password
# FACTSET_API_KEY=your_factset_api_key

# Enhanced Repositories Configuration (100% Open-Source)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key  # Optional - Free Tier Available
YAHOO_FINANCE_ENABLED=true
POLYGON_API_KEY=your_polygon_key  # Optional - Free Tier Available
QUANTCONNECT_API_KEY=your_quantconnect_key  # Optional - Free Tier Available
TECHNICAL_ANALYSIS_LIBRARY=talib
ML_ENABLED=true
ML_FRAMEWORK=scikit-learn

# NOTE: All core functionality works without optional API keys
```

### 3. Database Setup

#### PostgreSQL Setup

```bash
# Start PostgreSQL (using Docker)
docker run --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=veyra -p 5432:5432 postgres:15-alpine

# Create database
psql -h localhost -U postgres -d veyra -c "CREATE DATABASE veyra;"

# Run migrations
python -m alembic upgrade head
```

#### Redis Setup

```bash
# Start Redis (using Docker)
docker run --name redis -p 6379:6379 redis:7-alpine

# Test Redis connection
redis-cli ping
```

### 4. Development Server

#### Start Backend

```bash
# Start development server
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

# Start with debug mode
DEBUG=true uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Project Structure

### Backend Structure

```
src/backend/
├── main.py                 # FastAPI application entry point
├── api/                     # API routes and endpoints
│   ├── factset/           # FactSet integrations
│   ├── enhanced/           # Enhanced financial repositories
│   ├── financial_intelligence/  # Core API layer
│   └── websocket/           # Real-time data streaming
├── models/                  # Database models
├── services/                 # Business logic services
├── utils/                   # Utility functions
├── config/                   # Configuration management
└── tests/                    # Test suites
```

### Frontend Structure

```
src/frontend/
├── public/                   # Static assets
├── src/                      # React components
│   ├── components/            # Reusable UI components
│   ├── pages/                 # Page components
│   ├── hooks/                 # Custom React hooks
│   └── utils/                 # Frontend utilities
├── package.json               # Dependencies
└── vite.config.js             # Vite configuration
```

## Development Workflow

### 1. Code Quality

#### Linting

```bash
# Run Python linting
flake8 src/backend/
black src/backend/
isort src/backend/

# Run frontend linting
eslint src/frontend/src/
prettier src/frontend/src/
```

#### Testing

```bash
# Run backend tests
pytest src/backend/tests/ -v

# Run frontend tests
npm test

# Run integration tests
pytest tests/integration/ -v
```

### 2. Git Workflow

#### Branch Strategy

```bash
# Main branch for production
main

# Development branches
feature/factset-integration
feature/enhanced-repositories
feature/ai-ml-integration
bugfix/api-performance

# Release branches
release/v2.0.0
release/v2.1.0
```

#### Commit Convention

```bash
# Feature branch naming
feature/feature-name

# Commit message format
feat: Add FactSet real-time quotes integration
fix: Resolve API rate limiting issue
docs: Update API documentation
refactor: Optimize database queries
test: Add integration tests for enhanced APIs
```

## Development Tools

### VS Code Configuration

#### Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "bradlc.vscode-docker",
    "ms-vscode-remote",
    "gitlens.gitlens"
    "ms-vscode.test-adapter-converter"
    "github.copilot",
    "github.vscode-pull-request-github"
    "ms-vscode.hexeditor"
    "formulahendless.auto-close-brackets",
    "esbenp.prettier-vscode"
    "ms-vscode.vscode-json"
    "redhat.vscode-yaml"
    "ms-vscode-remote-containers"
    "ms-vscode.remote-explorer",
    "ms-vscode.remote-ssh",
    "ms-vscode.remote-server",
    "ms-vscode.remote-wsl"
    "ms-vscode-remote-repositories",
    "ms-vscode.remote-tunnels",
    "ms-vscode-remote-copilot",
    "ms-vscode-remote-debugger",
    "ms-vscode-remote-ssh-edit",
    "ms-vscode-remote-explorer",
    "ms-vscode-remote-testing",
    "ms-vscode-remote-server",
    "ms-vscode-remote-ports-forwarding",
    "ms-vscode-remote-startup",
    "ms-vscode-remote-wsl",
    "ms-vscode-remote-containers",
    "ms-vscode-remote-ssh",
    "ms-vscode-remote-ssh-edit",
    "ms-vscode-remote-debugger",
    "ms-vscode-remote-explorer",
    "ms-vscode-remote-testing",
    "ms-vscode-remote-ports-forwarding",
    "ms-vscode-remote-tunnels",
    "ms-vscode-remote-copilot",
    "ms-vscode-remote-ssh-edit",
    "ms-vscode-remote-wsl",
    "ms-vscode-remote-containers",
    "ms-vscode-remote-ssh",
    "ms-vscode-remote-ssh-edit",
    "ms-vscode-remote-debugger",
    "ms-vscode-remote-explorer",
    "ms-vscode-remote-testing"
  ]
}
```

#### Settings

```json
{
  "python.defaultInterpreterPath": "/usr/bin/python3",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.pycodestyleEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": true,
  "editor.rulers": true,
  "editor.wordWrap": "on",
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "git.enableSmartCommit": true,
  "git.autofetch": true,
  "git.confirmSync": false,
  "terminal.integrated.shell.linux": "/bin/bash"
}
```

### 3. Database Management

#### Alembic Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add enhanced repositories tables"

# Apply migration
alembic upgrade head

# Generate migration SQL
alembic upgrade head --sql

# Rollback migration
alembic downgrade -1
```

#### Database Tools

```bash
# Database console
psql -h localhost -U postgres -d veyra

# Redis console
redis-cli -h localhost -p 6379

# View database schema
alembic history --verbose
```

## API Development

### 1. Testing APIs

#### Local Testing

```python
# Test FactSet integration
import pytest
from src.backend.integrations.factset.financial_intelligence_layer import get_financial_intelligence_layer

@pytest.mark.asyncio
async def test_factset_real_time_quotes():
    config = {
        'factset': {
            'username': 'test_user',
            'password': 'test_pass',
            'api_key': 'test_key'
        }
    }
    
    financial_intelligence = get_financial_intelligence_layer(config)
    
    # Test real-time quotes
    quotes = await financial_intelligence.get_real_time_quotes(['AAPL'])
    
    assert len(quotes) > 0
    assert quotes[0]['symbol'] == 'AAPL'
    assert 'last_price' in quotes[0]
```

#### Mock Services

```python
# Mock external APIs for testing
from unittest.mock import AsyncMock

@pytest.fixture
def mock_factset_client():
    """Mock FactSet client for testing"""
    with AsyncMock() as mock_client:
        mock_client.get_portfolio_analytics.return_value = {
            'total_return': 0.15,
            'sharpe_ratio': 1.2
        }
        yield mock_client
```

### 2. API Documentation

#### OpenAPI Specification

```yaml
# OpenAPI configuration for documentation
openapi: 3.0.0
info:
  title: Veyra API
  description: Comprehensive financial platform with FactSet and enhanced integrations
  version: 2.0.0
  contact:
    name: Veyra Team
    email: api@veyra.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
servers:
  - url: https://api.veyra.com/v1
    description: Production server
  - url: https://api.veyra.com/staging/v1
    description: Staging server
```

### 3. Performance Optimization

#### Database Optimization

```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(DATABASE_URL, poolclass=QueuePool)
Session = sessionmaker(bind=engine)

# Query optimization
from sqlalchemy import text

# Use indexes for common queries
CREATE INDEX idx_symbols ON holdings(symbol);
CREATE INDEX idx_timestamps ON market_data(timestamp);

# Use EXPLAIN for slow queries
result = session.execute(text("EXPLAIN ANALYZE SELECT * FROM market_data WHERE symbol = :symbol").params(symbol='AAPL'))
```

#### Caching Strategy

```python
# Multi-level caching
from functools import lru_cache
import redis
import json

@lru_cache(maxsize=1000)
def get_cached_market_data(symbol):
    # Check cache first
    cache_key = f"market_data:{symbol}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Fetch from API if not cached
    data = await fetch_market_data(symbol)
    
    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(data))
    return data

# Cache invalidation
def invalidate_cache_pattern(pattern):
    """Invalidate cache by pattern"""
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
```

## Debugging

### 1. Common Issues

#### API Connection Problems

**Problem**: Cannot connect to FactSet APIs  
**Solution**:
1. Verify API credentials in environment variables
2. Check network connectivity to FactSet endpoints
3. Validate API key format and permissions
4. Check rate limiting status
5. Review FactSet service status page

#### Database Connection Issues

**Problem**: Database connection failed  
**Solution**:
1. Verify PostgreSQL service is running
2. Check database URL and credentials
3. Test connection with `psql` command
4. Check firewall settings for port 5432
5. Review PostgreSQL logs

#### Performance Issues

**Problem**: Slow API response times  
**Solution**:
1. Enable database query logging
2. Add performance monitoring
3. Implement proper caching
4. Use connection pooling
5. Optimize database queries with indexes

### 2. Debug Tools

#### Logging Configuration

```python
# Configure debug logging
import logging
import structlog

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log'),
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
)

logger = structlog.get_logger()
```

#### Performance Profiling

```python
# Enable profiling
import cProfile
import pstats

def profile_function(func):
    """Profile function performance"""
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        
        # Save stats
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        stats.print_stats()
        
        return result
    
    return wrapper
```

## Testing Strategy

### 1. Unit Testing

#### Backend Tests

```python
# Test FactSet integration
import pytest
from unittest.mock import AsyncMock, patch

class TestFactSetIntegration:
    @pytest.mark.asyncio
    async def test_real_time_quotes(self, mock_factset_client):
        """Test real-time quotes API"""
        with patch('src.backend.integrations.factset.enterprise_sdk_integration.get_factset_sdk') as mock_get_sdk:
            mock_get_sdk.return_value = AsyncMock()
            
            from src.backend.integrations.factset.enterprise_sdk_integration import get_factset_sdk
            with patch('src.backend.integrations.factset.financial_intelligence_layer.get_financial_intelligence_layer') as mock_get_layer:
                mock_get_layer.return_value = AsyncMock()
                
                financial_intelligence = get_financial_intelligence_layer(config)
                
                # Test the API call
                quotes = await financial_intelligence.get_real_time_quotes(['AAPL'])
                
                assert len(quotes) > 0
                assert quotes[0]['symbol'] == 'AAPL'
                assert 'last_price' in quotes[0]
    
    @pytest.mark.asyncio
    async def test_enhanced_repositories(self, mock_enhanced_repos):
        """Test enhanced repositories integration"""
        with patch('src.backend.integrations.additional.enhanced_financial_repositories.get_enhanced_repositories') as mock_get_repos:
            mock_get_repos.return_value = AsyncMock()
            
            from src.backend.integrations.additional.enhanced_financial_repositories import get_enhanced_repositories
            enhanced_repos = get_enhanced_repositories(config)
            
            # Test market data retrieval
            data = await enhanced_repos.get_enhanced_market_data('AAPL')
            
            assert data is not None
            assert len(data) > 0
```

#### Frontend Tests

```javascript
// Test React components
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('EnhancedMarketData', () => {
  it('should render market data correctly', async () => {
    const mockData = {
      symbol: 'AAPL',
      last_price: 150.25,
      volume: 1000000
    };
    
    render(<EnhancedMarketData data={mockData} />)
    
    // Check for price display
    expect(screen.getByText('150.25')).toBeInTheDocument();
  });
});
```

### 2. Integration Testing

#### End-to-End Tests

```python
# Test complete trading workflow
import pytest
import asyncio
from src.backend.integrations.factset.financial_intelligence_layer import get_financial_intelligence_layer
from src.backend.integrations.additional.enhanced_financial_repositories import get_enhanced_repositories

@pytest.mark.asyncio
async def test_complete_trading_workflow():
    """Test complete trading workflow"""
    config = TestConfig()
    
    financial_intelligence = get_financial_intelligence_layer(config)
    enhanced_repos = get_enhanced_repositories(config)
    
    # Test market data retrieval
    market_data = await financial_intelligence.get_real_time_quotes(['AAPL'])
    assert len(market_data) > 0
    
    # Test technical indicators
    indicators = await enhanced_repos.get_technical_indicators('AAPL', market_data)
    assert 'sma_20' in indicators
    assert 'rsi' in indicators
    
    # Test ML predictions
    predictions = await enhanced_repos.predict_prices_ml('AAPL', market_data)
    assert 'prediction' in predictions
    
    # Test backtesting
    backtest_result = await enhanced_repos.backtest_strategy('AAPL', {'short_window': 10, 'long_window': 50})
    assert backtest_result.total_return > 0
```

## Continuous Integration

### 1. CI/CD Pipeline

#### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest src/backend/tests/ -v
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t veyra:${{ github.sha }} .
      - name: Push to registry
        run: |
          docker push veyra:${{ github.sha }}
```

#### Docker Configuration

```dockerfile
# Dockerfile for multi-stage builds
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**Last Updated:** May 2026  
**Version:** 2.0.0  
**License:** MIT
