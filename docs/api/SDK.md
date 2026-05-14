# Veyra SDK Documentation

## JavaScript/TypeScript SDK

### Installation

```bash
npm install @veyra/sdk
```

### Usage

```typescript
import { VeyraClient } from '@veyra/sdk';

const client = new VeyraClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.veyra.com'
});

// Get market data
const quote = await client.market.getQuote('AAPL');
console.log(quote);

// Place an order
const order = await client.trading.placeOrder({
  symbol: 'AAPL',
  side: 'buy',
  quantity: 10,
  type: 'market'
});
```

## Python SDK

### Installation

```bash
pip install veyra-sdk
```

### Usage

```python
from veyra import VeyraClient

client = VeyraClient(
    api_key='your-api-key',
    base_url='https://api.veyra.com'
)

# Get market data
quote = client.market.get_quote('AAPL')
print(quote)

# Place an order
order = client.trading.place_order(
    symbol='AAPL',
    side='buy',
    quantity=10,
    type='market'
)
```

## Go SDK

### Installation

```bash
go get github.com/veyra/sdk-go
```

### Usage

```go
package main

import (
    "fmt"
    "github.com/veyra/sdk-go"
)

func main() {
    client := veyra.NewClient("your-api-key", "https://api.veyra.com")
    
    // Get market data
    quote, err := client.Market.GetQuote("AAPL")
    if err != nil {
        panic(err)
    }
    fmt.Println(quote)
}
```

## SDK Features

- Automatic authentication
- Retry logic
- Type safety (TypeScript/Go)
- WebSocket support
- Error handling
- Logging

## Configuration

### Common Options

```typescript
const client = new VeyraClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.veyra.com',
  timeout: 30000,
  retries: 3,
  logLevel: 'info'
});
```

## WebSocket Support

```typescript
const ws = await client.market.stream(['AAPL', 'GOOGL']);

ws.on('quote', (data) => {
  console.log('Received quote:', data);
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error);
});
```

## Error Handling

```typescript
try {
  const quote = await client.market.getQuote('AAPL');
} catch (error) {
  if (error instanceof VeyraAPIError) {
    console.error('API Error:', error.code, error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Advanced Usage

### Custom Headers

```typescript
const client = new VeyraClient({
  apiKey: 'your-api-key',
  headers: {
    'X-Custom-Header': 'value'
  }
});
```

### Request Interceptors

```typescript
client.addRequestInterceptor((config) => {
  console.log('Making request:', config.url);
  return config;
});

client.addResponseInterceptor((response) => {
  console.log('Received response:', response.status);
  return response;
});
```

## Support

For SDK-specific issues:
- JavaScript/TypeScript: https://github.com/veyra/sdk-js/issues
- Python: https://github.com/veyra/sdk-python/issues
- Go: https://github.com/veyra/sdk-go/issues
