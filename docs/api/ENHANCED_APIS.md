# Enhanced APIs Documentation

## Overview

This document provides comprehensive API reference for all enhanced financial repositories integrated with Veyra.

## Financial Intelligence Layer API

### Base URL
```
https://api.veyra.com/v1
```

### Authentication
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Core Endpoints

#### Market Data

##### Get Real-Time Quotes
```http
GET /market/realtime
Content-Type: application/json

Parameters:
- symbols (array, required): List of symbols
- source (string, optional): Data source (factset, alpha_vantage, yahoo, polygon)

Response:
```json
{
  "status": "success",
  "data": [
    {
      "symbol": "AAPL",
      "last_price": 150.25,
      "bid_price": 150.20,
      "ask_price": 150.30,
      "volume": 1000000,
      "timestamp": "2026-05-09T15:30:00Z",
      "source": "factset",
      "exchange": "NASDAQ",
      "currency": "USD"
    }
  ],
  "metadata": {
    "count": 1,
    "timestamp": "2026-05-09T15:30:00Z"
  }
}
```

##### Get Enhanced Market Data
```http
GET /market/enhanced/{symbol}
Content-Type: application/json

Parameters:
- symbol (string, required): Trading symbol
- start_date (string, required): Start date (YYYY-MM-DD)
- end_date (string, required): End date (YYYY-MM-DD)
- source (string, optional): Data source

Response:
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "historical_data": [
      {
        "timestamp": "2026-05-01T09:30:00Z",
        "price": 148.50,
        "volume": 1200000,
        "open_price": 148.00,
        "high_price": 149.00,
        "low_price": 147.50,
        "close_price": 148.50,
        "adj_close": 148.50,
        "source": "yahoo",
        "additional_fields": {
          "dividends": 0.92,
          "stock_splits": 0
        }
      }
    ],
    "technical_indicators": {
      "sma_20": 147.80,
      "sma_50": 145.20,
      "rsi": 65.5,
      "macd": 0.15,
      "bollinger_upper": 152.00,
      "bollinger_lower": 143.00
    },
    "ml_predictions": {
      "model_type": "random_forest",
      "prediction": 151.25,
      "confidence": 0.82,
      "last_price": 148.50,
      "prediction_change": 0.0187
    }
  }
}
```

#### Get Fundamentals Data
```http
GET /fundamentals/{symbol}
Content-Type: application/json

Parameters:
- symbol (string, required): Trading symbol
- periods (integer, optional): Number of periods (default: 4)
- statement_type (string, optional): income, balance, cash_flow

Response:
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "periods": [
      {
        "period_end": "2024-03-31",
        "fiscal_year": 2024,
        "fiscal_quarter": 1,
        "revenue": 119575000000,
        "net_income": 33916000000,
        "gross_profit": 72863000000,
        "operating_income": 45273000000,
        "ebitda": 51754000000,
        "total_assets": 352583000000,
        "total_liabilities": 290437000000,
        "shareholders_equity": 62146000000,
        "currency": "USD"
      }
    ]
  }
}
```

#### Get Advanced Risk Metrics
```http
GET /risk/advanced/{symbol}
Content-Type: application/json

Parameters:
- symbol (string, required): Trading symbol
- factor_model (string, optional): Factor model (default: fama_french_3_factor)

Response:
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "factor_exposures": {
      "market": 1.05,
      "size": -0.15,
      "value": 0.25,
      "momentum": 0.10
    },
    "factor_returns": {
      "market": 0.0008,
      "size": 0.0002,
      "value": 0.0001,
      "momentum": 0.0003
    },
    "var_1d": 0.02,
    "var_5d": 0.045,
    "var_30d": 0.089,
    "cvar_1d": 0.025,
    "beta": 1.05,
    "volatility": 0.15,
    "tracking_error": 0.04
  }
}
```

#### Get Estimates Data
```http
GET /estimates/{symbol}
Content-Type: application/json

Parameters:
- symbol (string, required): Trading symbol
- metrics (array, optional): List of metrics (default: ["eps", "revenue"])

Response:
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "estimates": [
      {
        "metric_name": "EPS",
        "fiscal_period": "2024Q4",
        "consensus_value": 5.25,
        "high_estimate": 5.50,
        "low_estimate": 5.00,
        "number_of_analysts": 25,
        "last_updated": "2026-05-08T14:30:00Z",
        "currency": "USD"
      },
      {
        "metric_name": "Revenue",
        "fiscal_period": "2024",
        "consensus_value": 385000000000,
        "high_estimate": 390000000000,
        "low_estimate": 380000000000,
        "number_of_analysts": 30,
        "last_updated": "2026-05-08T14:30:00Z",
        "currency": "USD"
      }
    ]
  }
}
```

#### Portfolio Optimization
```http
POST /portfolio/optimize
Content-Type: application/json

Parameters:
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "constraints": {
    "max_weight": 0.25,
    "min_return": 0.08,
    "max_risk": 0.20
  }
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "portfolio_id": "optimized_20260509_153000",
    "optimal_weights": {
      "AAPL": 0.35,
      "MSFT": 0.30,
      "GOOGL": 0.35
    },
    "expected_return": 0.12,
    "expected_risk": 0.15,
    "sharpe_ratio": 0.80,
    "constraints": {
      "max_weight": 0.25,
      "min_return": 0.08,
      "max_risk": 0.20
    },
    "optimization_date": "2026-05-09T15:30:00Z"
  }
}
```

#### Natural Language Processing
```http
POST /nlp/analyze
Content-Type: application/json

Parameters:
```json
{
  "text": "Apple announced strong Q4 earnings beating expectations",
  "analysis_types": ["sentiment", "entities", "topics"]
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "sentiment": {
      "score": 0.65,
      "label": "positive",
      "confidence": 0.82
    },
    "entities": [
      {
        "text": "Apple",
        "type": "ORGANIZATION",
        "confidence": 0.95
      },
      {
        "text": "Q4",
        "type": "DATE",
        "confidence": 0.88
      }
    ],
    "topics": [
      {
        "topic": "earnings",
        "confidence": 0.75
      },
      {
        "topic": "financial_performance",
        "confidence": 0.60
      }
    ],
    "confidence": 0.78,
    "processed_text": "Apple announced strong Q4 earnings beating expectations"
  }
}
```

#### Security Intelligence
```http
GET /intelligence/security/{symbol}
Content-Type: application/json

Parameters:
- symbol (string, required): Trading symbol

Response:
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "financial_standing": {
      "score": 0.75,
      "rating": "A-",
      "outlook": "Stable"
    },
    "stock_movements": {
      "trend": "bullish",
      "momentum": "strong",
      "volatility": "moderate"
    },
    "key_events": [
      {
        "type": "earnings",
        "date": "2026-05-08T00:00:00Z",
        "impact": "positive"
      },
      {
        "type": "analyst_meeting",
        "date": "2026-05-15T00:00:00Z",
        "impact": "neutral"
      }
    ],
    "risk_factors": {
      "market_risk": 0.3,
      "operational_risk": 0.2,
      "financial_risk": 0.1
    },
    "recommendations": [
      {
        "action": "BUY",
        "confidence": 0.82,
        "reason": "Strong fundamentals and positive sentiment"
      },
      {
        "action": "HOLD",
        "confidence": 0.15,
        "reason": "High valuation concerns"
      }
    ],
    "confidence": 0.78
  }
}
```

#### Mergers & Acquisitions
```http
GET /ma/data
Content-Type: application/json

Parameters:
- symbols (array, optional): List of symbols
- start_date (string, optional): Start date (YYYY-MM-DD)
- end_date (string, optional): End date (YYYY-MM-DD)

Response:
```json
{
  "status": "success",
  "data": [
    {
      "deal_id": "DEAL_001",
      "target": "Target Corp",
      "acquirer": "Acquirer Inc",
      "deal_type": "acquisition",
      "status": "announced",
      "announcement_date": "2026-05-01T00:00:00Z",
      "value": 5000000000,
      "currency": "USD",
      "premium": 0.25
    }
  ]
}
```

#### Quantitative Factors
```http
GET /quant/factors/{universe}
Content-Type: application/json

Parameters:
- universe (string, optional): Factor universe (default: global_equity)

Response:
```json
{
  "status": "success",
  "data": {
    "factor_definitions": [
      {
        "name": "book_to_market",
        "description": "Book value to market ratio"
      },
      {
        "name": "price_momentum_12m",
        "description": "12-month price momentum"
      },
      {
        "name": "roe",
        "description": "Return on equity"
      },
      {
        "name": "volatility_12m",
        "description": "12-month historical volatility"
      }
    ],
    "factor_returns": {
      "2024-01": {
        "value": 0.02,
        "momentum": 0.03,
        "quality": 0.01,
        "volatility": 0.15
      },
      "2024-02": {
        "value": 0.01,
        "momentum": 0.02,
        "quality": 0.02,
        "volatility": 0.12
      }
    },
    "factor_correlations": {
      "value_momentum": 0.15,
      "value_quality": 0.35,
      "momentum_quality": -0.10
    },
    "universe": "global_equity",
    "last_updated": "2026-05-09T15:30:00Z"
  }
}
```

#### Conversational AI
```http
POST /ai/conversational
Content-Type: application/json

Parameters:
```json
{
  "query": "What's Apple's valuation?",
  "context": {
    "user_portfolio": ["AAPL", "MSFT"],
    "time_horizon": "1_year",
    "risk_tolerance": "moderate"
  }
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "answer": "Based on current fundamentals and market conditions, Apple appears fairly valued with a P/E ratio of 28.5, slightly above the industry average of 25.0. The company's strong cash flow generation and consistent dividend growth support this valuation.",
    "confidence": 0.85,
    "sources": [
      "FactSet Fundamentals",
      "FactSet Estimates",
      "Market Data"
    ],
    "follow_up_questions": [
      "Would you like to see a detailed DCF analysis?",
      "Are you interested in scenario analysis for different growth rates?"
    ],
    "query_type": "valuation_analysis"
  }
}
```

## Technical Analysis Endpoints

#### Get Technical Indicators
```http
GET /technical/indicators/{symbol}
Content-Type: application/json

Parameters:
- symbol (string, required): Trading symbol
- indicators (array, required): List of indicators
- period (integer, optional): Period for calculations (default: 20)

Response:
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "indicators": {
      "sma_20": [
        {
          "timestamp": "2026-05-09T15:30:00Z",
          "indicator_name": "SMA_20",
          "value": 147.80,
          "signal": "HOLD",
          "confidence": 0.7,
          "source": "talib"
        }
      ],
      "rsi": [
        {
          "timestamp": "2026-05-09T15:30:00Z",
          "indicator_name": "RSI",
          "value": 65.5,
          "signal": "HOLD",
          "confidence": 0.8,
          "source": "talib"
        }
      ],
      "macd": [
        {
          "timestamp": "2026-05-09T15:30:00Z",
          "indicator_name": "MACD",
          "value": 0.15,
          "signal": "BUY",
          "confidence": 0.75,
          "source": "talib"
        }
      ],
      "bollinger": [
        {
          "timestamp": "2026-05-09T15:30:00Z",
          "indicator_name": "Bollinger_Upper",
          "value": 152.00,
          "signal": "HOLD",
          "confidence": 0.7,
          "source": "talib"
        }
      ]
    }
  }
}
```

#### Backtest Strategy
```http
POST /backtest/strategy
Content-Type: application/json

Parameters:
```json
{
  "symbol": "AAPL",
  "strategy_config": {
    "short_window": 10,
    "long_window": 50,
    "position_size": 10000
  },
  "start_date": "2025-01-01",
  "end_date": "2026-05-09"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "strategy_name": "SMA_Crossover_10_50",
    "symbol": "AAPL",
    "start_date": "2025-01-01T00:00:00Z",
    "end_date": "2026-05-09T00:00:00Z",
    "total_return": 0.15,
    "annualized_return": 0.12,
    "sharpe_ratio": 0.80,
    "max_drawdown": -0.12,
    "win_rate": 0.65,
    "total_trades": 25,
    "benchmark_return": 0.08,
    "alpha": 0.07
  }
}
```

## WebSocket API

### Real-Time Data Stream
```javascript
// WebSocket connection for real-time data
const ws = new WebSocket('wss://api.veyra.com/v1/ws/market');

ws.onopen = function() {
    console.log('Connected to real-time market data');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'quote') {
        updateQuoteDisplay(data.payload);
    } else if (data.type === 'trade') {
        updateTradeDisplay(data.payload);
    } else if (data.type === 'indicator') {
        updateIndicatorDisplay(data.payload);
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function() {
    console.log('WebSocket connection closed');
};
```

### Subscribe to Real-Time Data
```javascript
// Subscribe to real-time data for specific symbols
const subscription = {
    action: 'subscribe',
    symbols: ['AAPL', 'MSFT', 'GOOGL'],
    data_types: ['quotes', 'indicators', 'signals']
};

ws.send(JSON.stringify(subscription));
```

## Error Handling

### Standard Error Response Format
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "Symbol 'INVALID' not found",
    "details": {
      "symbol": "INVALID",
      "requested_at": "2026-05-09T15:30:00Z"
    }
  },
  "metadata": {
    "timestamp": "2026-05-09T15:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Error Codes
- `INVALID_SYMBOL`: Symbol not found or invalid
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `INSUFFICIENT_PERMISSIONS`: Missing required permissions
- `DATA_UNAVAILABLE`: Data temporarily unavailable
- `VALIDATION_ERROR`: Request validation failed
- `INTERNAL_ERROR`: Internal server error

## Rate Limiting

### Rate Limits by Endpoint
| Endpoint | Rate Limit | Time Window |
|-----------|-------------|-------------|
| Real-Time Quotes | 100 requests/minute | 1 minute |
| Enhanced Market Data | 1000 requests/hour | 1 hour |
| Technical Indicators | 500 requests/minute | 1 minute |
| Portfolio Optimization | 10 requests/minute | 1 minute |
| NLP Analysis | 50 requests/minute | 1 minute |
| WebSocket Connections | 10 connections/user | Concurrent |

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 2026-05-09T16:00:00Z
```

## SDK and Libraries

### Python SDK
```python
# Install the Veyra Python SDK
pip install veyra-sdk

# Initialize the client
from financial_master_sdk import FinancialMasterClient

client = FinancialMasterClient(
    api_key='your_api_key',
    base_url='https://api.veyra.com/v1'
)

# Get real-time quotes
quotes = await client.get_real_time_quotes(['AAPL', 'MSFT'])

# Get fundamentals
fundamentals = await client.get_fundamentals_data(['AAPL', 'MSFT'])

# Technical analysis
indicators = await client.get_technical_indicators('AAPL', ['sma', 'rsi', 'macd'])

# Portfolio optimization
optimization = await client.optimize_portfolio_advanced(['AAPL', 'MSFT', 'GOOGL'])
```

### JavaScript SDK
```javascript
// Install the Veyra JavaScript SDK
npm install veyra-sdk

// Initialize the client
import { FinancialMasterClient } from 'veyra-sdk';

const client = new FinancialMasterClient({
    apiKey: 'your_api_key',
    baseUrl: 'https://api.veyra.com/v1'
});

// Get real-time quotes
const quotes = await client.getRealTimeQuotes(['AAPL', 'MSFT']);

// Get fundamentals
const fundamentals = await client.getFundamentals(['AAPL', 'MSFT']);

// Technical analysis
const indicators = await client.getTechnicalIndicators('AAPL', ['sma', 'rsi', 'macd']);

// Portfolio optimization
const optimization = await client.optimizePortfolio(['AAPL', 'MSFT', 'GOOGL']);
```

### React Components
```jsx
// Veyra React Components
import { 
  RealTimeChart, 
  TechnicalIndicators, 
  PortfolioOptimizer,
  MarketDataTable 
} from 'veyra-ui';

function TradingDashboard() {
  return (
    <div>
      <RealTimeChart symbols={['AAPL', 'MSFT', 'GOOGL']} />
      <TechnicalIndicators symbol="AAPL" indicators={['sma', 'rsi', 'macd']} />
      <PortfolioOptimizer symbols={['AAPL', 'MSFT', 'GOOGL']} />
      <MarketDataTable symbol="AAPL" />
    </div>
  );
}
```

## Testing

### API Testing Examples
```python
# Unit tests for enhanced APIs
import pytest
from financial_master_sdk.testing import APITestCase

class TestEnhancedAPIs(APITestCase):
    async def test_real_time_quotes(self):
        response = await self.client.get_real_time_quotes(['AAPL'])
        assert response.status == 'success'
        assert len(response.data) > 0
        assert 'symbol' in response.data[0]
    
    async def test_technical_indicators(self):
        indicators = await self.client.get_technical_indicators('AAPL', ['sma', 'rsi'])
        assert 'sma' in indicators
        assert 'rsi' in indicators
        assert indicators['sma'][0]['confidence'] > 0
    
    async def test_portfolio_optimization(self):
        optimization = await self.client.optimize_portfolio(['AAPL', 'MSFT'])
        assert optimization['status'] == 'success'
        assert 'optimal_weights' in optimization
        assert optimization['sharpe_ratio'] > 0

# Run tests
pytest tests/test_enhanced_apis.py -v
```

### Integration Testing
```python
# Integration tests for complete workflows
import asyncio
from financial_master_sdk import FinancialMasterClient

async def test_complete_trading_workflow():
    client = FinancialMasterClient(api_key='test_key')
    
    # 1. Get market data
    market_data = await client.get_enhanced_market_data('AAPL', 
        datetime.now() - timedelta(days=30), datetime.now())
    
    # 2. Calculate technical indicators
    indicators = await client.get_technical_indicators('AAPL', ['sma', 'rsi', 'macd'])
    
    # 3. Run ML prediction
    prediction = await client.predict_prices_ml('AAPL', market_data)
    
    # 4. Backtest strategy
    backtest = await client.backtest_strategy('AAPL', {'short_window': 10, 'long_window': 50},
        datetime.now() - timedelta(days=365), datetime.now())
    
    # 5. Optimize portfolio
    optimization = await client.optimize_portfolio_advanced(['AAPL', 'MSFT', 'GOOGL'])
    
    # 6. Get sentiment analysis
    sentiment = await client.get_market_sentiment('AAPL')
    
    return {
        'market_data': market_data,
        'indicators': indicators,
        'prediction': prediction,
        'backtest': backtest,
        'optimization': optimization,
        'sentiment': sentiment
    }

# Run integration test
result = asyncio.run(test_complete_trading_workflow())
print(f"Integration test completed: {result}")
```

## Monitoring and Analytics

### Health Check Endpoint
```http
GET /health
Content-Type: application/json

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-09T15:30:00Z",
  "version": "2.0.0",
  "services": {
    "financial_intelligence_layer": "healthy",
    "factset_apis": "healthy",
    "enhanced_repositories": "healthy",
    "database": "healthy",
    "cache": "healthy",
    "external_apis": "healthy"
  },
  "metrics": {
    "api_response_time": 0.045,
    "requests_per_minute": 150,
    "error_rate": 0.001,
    "uptime": 99.99
  }
}
```

### Performance Metrics
```http
GET /metrics
Content-Type: application/json

Response:
```json
{
  "status": "success",
  "data": {
    "api_performance": {
      "avg_response_time": 0.045,
      "p95_response_time": 0.120,
      "p99_response_time": 0.250,
      "requests_per_second": 2.5,
      "error_rate": 0.001
    },
    "database_performance": {
      "query_time_avg": 0.025,
      "connections_active": 15,
      "cache_hit_rate": 0.85
    },
    "system_performance": {
      "cpu_usage": 0.45,
      "memory_usage": 0.62,
      "disk_usage": 0.35
    }
  }
}
```

---

**Last Updated:** May 2026  
**Version:** 2.0.0  
**License:** MIT
