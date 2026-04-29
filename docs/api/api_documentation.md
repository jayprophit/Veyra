# Financial Master API Documentation

## Overview

The Financial Master API provides unified access to all system capabilities through a RESTful interface with WebSocket support for real-time data.

**Base URL:** `http://localhost:8000/api/v1`

**WebSocket Endpoint:** `ws://localhost:8000/ws/v1/market`

---

## Authentication

All API requests require a Bearer token in the Authorization header:

```
Authorization: Bearer <your-token>
```

### Example

```bash
curl -H "Authorization: Bearer test-token" \
     http://localhost:8000/api/v1/portfolio
```

---

## Market Data Endpoints

### Get Quote

Retrieve real-time quote for a symbol.

**Endpoint:** `GET /market/quote/{symbol}`

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "change": 1.5,
  "change_pct": 1.01,
  "volume": 15000000,
  "timestamp": "2026-01-15T14:30:00"
}
```

### Get Historical Data

Retrieve historical price data.

**Endpoint:** `GET /market/historical/{symbol}?timeframe=1d&days=30`

**Parameters:**
- `timeframe`: Data interval (1d, 1h, 15m)
- `days`: Number of days of history

---

## Trading Endpoints

### Create Order

Submit a new order.

**Endpoint:** `POST /orders`

**Request Body:**
```json
{
  "symbol": "AAPL",
  "side": "buy",
  "quantity": "100",
  "order_type": "limit",
  "price": "150.00",
  "time_in_force": "day"
}
```

**Response:**
```json
{
  "order_id": "ORD-12345",
  "status": "pending",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": "100",
  "filled_qty": "0",
  "avg_price": null,
  "created_at": "2026-01-15T14:30:00"
}
```

### List Orders

Get list of orders with optional filters.

**Endpoint:** `GET /orders?status=open&limit=100`

### Cancel Order

Cancel an existing order.

**Endpoint:** `DELETE /orders/{order_id}`

---

## Portfolio Endpoints

### Get Portfolio Summary

Retrieve complete portfolio information.

**Endpoint:** `GET /portfolio`

**Response:**
```json
{
  "total_value": "100000.00",
  "cash_balance": "25000.00",
  "positions_value": "75000.00",
  "day_pnl": "500.00",
  "total_pnl": "5000.00",
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": "100",
      "avg_cost": "145.00",
      "current_price": "150.25",
      "market_value": "15025.00",
      "unrealized_pnl": "525.00",
      "unrealized_pnl_pct": 3.62
    }
  ]
}
```

### Get Positions

Get current positions only.

**Endpoint:** `GET /portfolio/positions`

---

## AI Analysis Endpoints

### Run Analysis

Execute AI analysis on a symbol.

**Endpoint:** `POST /analysis`

**Request Body:**
```json
{
  "symbol": "AAPL",
  "analysis_type": "sentiment",
  "timeframe": "1d"
}
```

**Analysis Types:**
- `sentiment` - News and social sentiment
- `pattern` - Technical pattern recognition
- `prediction` - Price prediction (LSTM)
- `risk` - Risk analysis

**Response:**
```json
{
  "symbol": "AAPL",
  "analysis_type": "sentiment",
  "result": {
    "sentiment": "bullish",
    "score": 0.75,
    "sources": ["news", "social"]
  },
  "confidence": 0.82,
  "generated_at": "2026-01-15T14:30:00"
}
```

### Get Sentiment

Quick sentiment check for a symbol.

**Endpoint:** `GET /analysis/sentiment/{symbol}`

---

## Risk Management Endpoints

### Get Risk Metrics

Retrieve portfolio risk metrics.

**Endpoint:** `GET /risk/metrics`

**Response:**
```json
{
  "portfolio_var": 2500.00,
  "portfolio_var_pct": 2.5,
  "sharpe_ratio": 1.5,
  "max_drawdown": 5.0,
  "beta": 1.0,
  "correlation_matrix": {
    "AAPL": {"MSFT": 0.8, "GOOGL": 0.7},
    "MSFT": {"AAPL": 0.8, "GOOGL": 0.75}
  }
}
```

### Run Stress Test

Execute portfolio stress test.

**Endpoint:** `POST /risk/stress-test`

**Request Body:**
```json
{
  "scenarios": ["market_crash", "interest_rate_spike", "recession"]
}
```

---

## System Endpoints

### Get System Status

Check system health and module status.

**Endpoint:** `GET /system/status`

**Response:**
```json
{
  "status": "healthy",
  "version": "2.50.0",
  "uptime_seconds": 3600,
  "modules": {
    "market_data": "running",
    "execution": "running",
    "portfolio": "running",
    "risk_engine": "running",
    "ai_analysis": "running"
  },
  "health_score": 0.98
}
```

### Restart Module

Restart a specific system module.

**Endpoint:** `POST /system/modules/{module_name}/restart`

---

## WebSocket API

### Connection

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/v1/market');

ws.onopen = () => {
  // Subscribe to streams
  ws.send(JSON.stringify({
    action: 'subscribe',
    streams: ['prices', 'orders', 'portfolio']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Message Types

**Subscribe:**
```json
{
  "action": "subscribe",
  "streams": ["prices", "orders", "alerts"]
}
```

**Unsubscribe:**
```json
{
  "action": "unsubscribe",
  "streams": ["prices"]
}
```

**Heartbeat:**
```json
{
  "action": "ping"
}
```

### Stream Data Formats

**Price Update:**
```json
{
  "stream": "prices",
  "type": "update",
  "data": {
    "symbol": "AAPL",
    "price": 150.25,
    "change": 1.5,
    "timestamp": "2026-01-15T14:30:00"
  },
  "timestamp": "2026-01-15T14:30:00",
  "sequence": 12345
}
```

**Order Update:**
```json
{
  "stream": "orders",
  "type": "update",
  "data": {
    "order_id": "ORD-12345",
    "status": "filled",
    "filled_qty": 100,
    "timestamp": "2026-01-15T14:30:00"
  }
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-15T14:30:00"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `503` - Service Unavailable (module not running)

---

## Rate Limits

- REST API: 1000 requests per minute
- WebSocket: 1 message per second (ping excluded)

---

## SDK Examples

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"
HEADERS = {"Authorization": "Bearer test-token"}

# Get portfolio
response = requests.get(f"{API_URL}/portfolio", headers=HEADERS)
portfolio = response.json()

# Create order
order = {
    "symbol": "AAPL",
    "side": "buy",
    "quantity": "100",
    "order_type": "market"
}
response = requests.post(f"{API_URL}/orders", json=order, headers=HEADERS)
```

### JavaScript

```javascript
// Get quote
fetch('http://localhost:8000/api/v1/market/quote/AAPL', {
  headers: { 'Authorization': 'Bearer test-token' }
})
.then(response => response.json())
.then(data => console.log(data));

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/v1/market');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    streams: ['prices']
  }));
};
```

---

## Module Reference

| Module | Status | Capabilities |
|--------|--------|--------------|
| Market Data | ✅ Running | Real-time quotes, historical data |
| Execution | ✅ Running | Order routing, smart order router |
| Portfolio | ✅ Running | Position tracking, P&L calculation |
| Risk Engine | ✅ Running | VaR, stress testing, correlations |
| AI Analysis | ✅ Running | Sentiment, patterns, predictions |
| Crisis Detector | ✅ Running | VIX, credit stress, contagion |
| Stat Arb | ✅ Running | Pairs trading, cointegration |
| Biometrics | ✅ Running | Stress monitoring, position sizing |

---

**Version:** 2.50.0
**Last Updated:** January 2026

