# Veyra API Documentation

## Overview

The Veyra API provides a RESTful interface for accessing financial data, managing portfolios, executing trades, and integrating AI/ML capabilities. This document describes the API structure, authentication, and available endpoints.

## Base URL

```
Development: http://localhost:8000/api/v1
Staging: https://staging.veyra.com/api/v1
Production: https://api.veyra.com/api/v1
```

## Authentication

All API requests require authentication using JWT tokens.

### Getting a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:

```json
{
  "access_token": "<access-token>",
  "refresh_token": "<refresh-token>",
  "expires_in": 3600
}
```

### Using the Token

Include the token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

## Rate Limiting

- **Default**: 100 requests per minute
- **Authenticated**: 1000 requests per minute
- **WebSocket**: No rate limiting (connection-based)

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1634567890
```

## API Endpoints

### Authentication

#### Login
```http
POST /api/v1/auth/login
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
```

#### Logout
```http
POST /api/v1/auth/logout
```

### Market Data

#### Get Quote
```http
GET /api/v1/market/quote/{symbol}
```

#### Get Historical Data
```http
GET /api/v1/market/historical/{symbol}
```

#### Get Real-time Data (WebSocket)
```http
WS /api/v1/market/stream
```

### Portfolio

#### Get Portfolio
```http
GET /api/v1/portfolio
```

#### Update Portfolio
```http
PUT /api/v1/portfolio
```

#### Get Performance
```http
GET /api/v1/portfolio/performance
```

### Trading

#### Place Order
```http
POST /api/v1/trading/orders
```

#### Get Orders
```http
GET /api/v1/trading/orders
```

#### Cancel Order
```http
DELETE /api/v1/trading/orders/{order_id}
```

### Analytics

#### Get Technical Indicators
```http
GET /api/v1/analytics/indicators/{symbol}
```

#### Get Analysis
```http
POST /api/v1/analytics/analyze
```

### AI/ML

#### Get AI Prediction
```http
POST /api/v1/ai/predict
```

#### Get Sentiment Analysis
```http
POST /api/v1/ai/sentiment
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Common Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.veyra.com/api/v1/market/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['AAPL', 'GOOGL', 'MSFT']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### WebSocket Message Format

```json
{
  "type": "quote",
  "symbol": "AAPL",
  "price": 150.25,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## SDK

Veyra provides official SDKs for:

- JavaScript/TypeScript
- Python
- Go

See the [SDK documentation](./SDK.md) for details.

## Support

For API support, contact:
- Email: api@veyra.com
- Documentation: https://docs.veyra.com
- Status Page: https://status.veyra.com
