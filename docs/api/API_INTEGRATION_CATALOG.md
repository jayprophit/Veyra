# Financial Master - API Integration Catalog

## Overview

This document provides a comprehensive catalog of all APIs integrated or planned for the Financial Master platform, organized by category with **Free Tier** and **Paid Tier** options.

---

## Table of Contents

1. [Market Data APIs](#1-market-data-apis)
2. [Trading & Brokerage APIs](#2-trading--brokerage-apis)
3. [Fiat & Forex APIs](#3-fiat--forex-apis)
4. [Cryptocurrency APIs](#4-cryptocurrency-apis)
5. [Banking & Account Aggregation](#5-banking--account-aggregation)
6. [Alternative Data & ESG](#6-alternative-data--esg)
7. [News & Sentiment APIs](#7-news--sentiment-apis)
8. [LLM & AI APIs](#8-llm--ai-apis)
9. [Precious Metals & Commodities](#9-precious-metals--commodities)
10. [Regulatory & Compliance APIs](#10-regulatory--compliance-apis)
11. [Implementation Status](#11-implementation-status)
12. [API Key Management](#12-api-key-management)

---

## 1. Market Data APIs

### 1.1 Stocks, ETFs, Equities

| Provider | Tier | Cost | Limits | Use Case | Implementation |
|----------|------|------|--------|----------|----------------|
| **Polygon.io** | Free | $0 | 5 API calls/min | Real-time trades, quotes, aggregates | `@/src/backend/app/data_providers/polygon_provider.py` |
| **Polygon.io** | Paid | $49-499/mo | Up to 100K calls/min | Professional trading, WebSocket streaming | Same |
| **Alpaca Data** | Free | $0 | 200 requests/min | US stocks, ETFs, crypto | `@/src/backend/app/brokers/alpaca_client.py` |
| **Alpaca Data** | Paid | $9-99/mo | Higher limits | Unlimited data, SIP feed | Same |
| **Alpha Vantage** | Free | $0 | 5 calls/min, 500/day | Historical data, fundamentals | `@/src/backend/app/config.py` |
| **Alpha Vantage** | Paid | $49-199/mo | 75-1200 calls/min | Real-time, premium data | Same |
| **Yahoo Finance** | Free | $0 | Unofficial, rate limited | Historical data, splits, dividends | Via `yfinance` library |
| **IEX Cloud** | Free | $0 | 50K messages/mo | US equities, fundamentals | Not implemented |
| **IEX Cloud** | Paid | $9-199/mo | Up to 100M messages | Real-time, intraday | Not implemented |
| **Twelve Data** | Free | $0 | 800 calls/day | Stocks, forex, crypto | Not implemented |
| **Twelve Data** | Paid | $29-199/mo | Up to 10M calls/mo | Real-time, WebSocket | Not implemented |
| **Quandl/NASDAQ** | Mixed | Varies | Dataset dependent | Alternative data, futures | Not implemented |

### 1.2 Bonds & Fixed Income

| Provider | Tier | Cost | Limits | Use Case | Implementation |
|----------|------|------|--------|----------|----------------|
| **FRED (Federal Reserve)** | Free | $0 | 120 requests/min | Treasury yields, economic indicators | Via `pandas_datareader` |
| **FINRA TRACE** | Free | $0 | Registration required | Corporate bond trades | Not implemented |
| **Treasury Direct** | Free | $0 | Rate limited | US government securities | Not implemented |
| **MSRB EMMA** | Free | $0 | Public access | Municipal bond data | Not implemented |
| **Bloomberg API** | Paid | $$$ | Enterprise | Comprehensive fixed income | Not implemented |
| **Refinitiv (LSEG)** | Paid | $$$ | Enterprise | Bond analytics, pricing | Not implemented |

### 1.3 Options & Futures

| Provider | Tier | Cost | Limits | Use Case | Implementation |
|----------|------|------|--------|----------|----------------|
| **Polygon.io Options** | Paid | $99+/mo | Included in plan | Options flow, Greeks | `@/src/backend/app/data_providers/polygon_provider.py` |
| **CBOE LiveVol** | Paid | $$$ | Enterprise | Options analytics | Not implemented |
| **Interactive Brokers** | Free/Paid | $0* | Requires account | Futures, options trading | `@/src/backend/app/brokers/interactive_brokers_real.py` |

---

## 2. Trading & Brokerage APIs

### 2.1 US Equity Brokers

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **Alpaca** | Free (Paper) | $0 | Paper trading, fractional shares | `@/src/backend/app/brokers/alpaca_client.py` |
| **Alpaca** | Live | Commission-free | Real trading, $1 minimum | Same |
| **Interactive Brokers** | Free (Paper) | $0 | Global markets, options, futures | `@/src/backend/app/brokers/interactive_brokers_real.py` |
| **Interactive Brokers** | Live | Low commissions | Professional execution | Same |
| **Trading212** | Free | $0 | EU/UK focused, CFDs | `@/src/backend/app/brokers/trading212_client.py` |

### 2.2 CFD & Forex Brokers

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **MetaTrader5** | Free | $0 | Forex, CFDs, automated trading | `@/src/backend/app/brokers/metatrader5_bridge.py` |
| **OANDA** | Free (Practice) | $0 | Forex practice account | `@/src/backend/app/exchanges/fiat_exchanges.py` |
| **OANDA** | Live | Spread only | Forex trading | Same |
| **Forex.com** | Free/Paid | Varies | Major/minor currency pairs | Same |

---

## 3. Fiat & Forex APIs

### 3.1 Currency Exchange

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **Wise (TransferWise)** | Free | $0 | Rate comparison, quotes | `@/src/backend/app/exchanges/fiat_exchanges.py` |
| **Wise** | Per transaction | 0.5% + fee | International transfers | Same |
| **Open Exchange Rates** | Free | $0 | 1000 requests/mo, hourly updates | Not implemented |
| **Open Exchange Rates** | Paid | $12-97/mo | Real-time, unlimited | Not implemented |
| **XE Currency API** | Free trial | $0 | 100 requests/day | Not implemented |
| **XE Currency API** | Paid | $799+/yr | Real-time rates | Not implemented |
| **Fixer.io** | Free | $0 | 100 requests/day, EUR base | Not implemented |
| **Fixer.io** | Paid | $10-99/mo | 10K-500K requests | Not implemented |

---

## 4. Cryptocurrency APIs

### 4.1 Spot Exchanges

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **Binance** | Free | $0 | Spot trading, up to 1200 WAPI weight/min | `@/src/backend/app/exchanges/crypto_exchanges.py` |
| **Binance** | VIP | Fee discounts | Higher limits, priority support | Same |
| **Coinbase Pro** | Free | $0 | Advanced trading, lower fees | `@/src/backend/app/brokers/coinbase_real.py` |
| **Coinbase** | Paid | 0.5% spread | Simple buy/sell | Same |
| **Kraken** | Free | $0 | Spot, margin, futures | Not implemented |
| **KuCoin** | Free | $0 | Spot, margin, lending | Not implemented |
| **Gemini** | Free | $0 | Regulated, secure | Not implemented |

### 4.2 Data Providers

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **CoinGecko** | Free | $0 | 10-30 calls/min, market data | Not implemented |
| **CoinGecko** | Paid | $129+/mo | Higher limits, pro data | Not implemented |
| **CoinMarketCap** | Free | $0 | 10K calls/mo, basic data | Not implemented |
| **CoinMarketCap** | Paid | $79+/mo | Historical data, pro features | Not implemented |
| **CryptoCompare** | Free | $0 | 100K calls/mo | Not implemented |
| **CryptoCompare** | Paid | $79+/mo | Real-time, enterprise | Not implemented |

---

## 5. Banking & Account Aggregation

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **Plaid** | Sandbox | $0 | Test environment, 100 institutions | `@/src/backend/app/bank_sync_plaid.py` |
| **Plaid** | Production | Pay-as-you-go | 12,000+ institutions, transactions | Same |
| **Plaid** | Scale | Custom pricing | Enterprise features | Same |
| **Yodlee** | Paid | $$$ | Bank aggregation, verification | Not implemented |
| **TrueLayer** | Free | £0 | EU/UK open banking | Not implemented |
| **TrueLayer** | Paid | Pay-per-use | Data + payments | Not implemented |
| **Finicity** | Paid | $$ | Credit decisioning, verification | Not implemented |
| **MX** | Paid | $$ | Financial data, analytics | Not implemented |

---

## 6. Alternative Data & ESG

### 6.1 ESG Data

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **MSCI ESG** | Paid | $$$ | Industry standard ratings | `@/src/backend/app/esg/providers.py` |
| **Sustainalytics** | Paid | $$$ | Risk-based ESG ratings | Same |
| **Refinitiv ESG** | Paid | $$$ | Quantitative ESG metrics | Same |
| **ESG Enterprise** | Free | $0 | Basic ESG scores | Not implemented |
| **ESG Enterprise** | Paid | $49+/mo | Full API access | Not implemented |

### 6.2 Alternative Data

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **SEC EDGAR** | Free | $0 | Filings, 10-K, 10-Q, 13F | `@/src/backend/app/insider_monitor/form4_analyzer.py` |
| **OpenFIGI** | Free | $0 | Instrument identification | Not implemented |
| **FRED (St. Louis Fed)** | Free | $0 | Economic data, 120 req/min | Via `pandas_datareader` |
| **World Bank API** | Free | $0 | Global economic indicators | Not implemented |
| **IMF Data API** | Free | $0 | International financial stats | Not implemented |

---

## 7. News & Sentiment APIs

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **NewsAPI** | Free | $0 | 100 requests/day | `@/src/backend/app/sentiment/news_sentiment_engine.py` |
| **NewsAPI** | Paid | $449+/mo | 1M requests, headlines | Same |
| **Twitter/X API** | Free | $0 | 100 tweets/month read | `@/src/backend/app/social_sentiment/twitter_analyzer.py` |
| **Twitter/X API** | Basic | $100/mo | 10K tweets/month | Same |
| **Twitter/X API** | Pro | $5000/mo | 1M tweets/month, real-time | Same |
| **Reddit API** | Free | $0 | 100 queries/min | `@/src/backend/app/social_sentiment/reddit_analyzer.py` |
| **Reddit API** | Paid | Custom | Higher limits, commercial use | Same |
| **Finnhub** | Free | $0 | 60 calls/min, news, sentiment | Not implemented |
| **Finnhub** | Paid | $10-200/mo | Real-time, websocket | Not implemented |
| **Benzinga** | Free | $0 | 100 calls/day | Not implemented |
| **Benzinga** | Paid | $47-297/mo | Real-time news, options | Not implemented |

---

## 8. LLM & AI APIs

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **Ollama (Local)** | Free | $0 | Local inference, unlimited | `@/src/backend/app/llm_integration_free_tier.py` |
| **Groq** | Free | $0 | 20 requests/min, Llama3, Mixtral | Same |
| **Groq** | Paid | $0.10/M tokens | High-speed inference | Same |
| **OpenAI** | Paid | $0.15-5/M tokens | GPT-4o, GPT-4o-mini | Same |
| **Anthropic** | Paid | $0.25-3/M tokens | Claude 3 Haiku/Sonnet/Opus | Same |
| **Mistral AI** | Free | $0 | Limited tier available | Not implemented |
| **Mistral AI** | Paid | Usage-based | Commercial models | Not implemented |
| **Google Gemini** | Free | $0 | 60 requests/min | Not implemented |
| **Google Gemini** | Paid | Usage-based | Pro features | Not implemented |
| **Hugging Face** | Free | $0 | Inference API, 30K chars/month | `@/src/backend/app/ai/huggingface_integration.py` |
| **Hugging Face** | Paid | $0.60/hour | Dedicated inference | Same |

---

## 9. Precious Metals & Commodities

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **GoldAPI.io** | Free | $0 | 100 requests/day | `@/src/backend/app/physical_metals/metals_tracker.py` |
| **GoldAPI.io** | Paid | $5-49/mo | Up to 300K requests | Same |
| **Metals-API.com** | Free | $0 | 50 requests/day, base metals | Same |
| **Metals-API.com** | Paid | $19-149/mo | Historical, 100K requests | Same |
| **Kitco** | Free | $0 | Web scraping (unofficial) | Same |
| **ICE Data Services** | Paid | $$$ | Professional commodities | Not implemented |
| **CME Group** | Free/Paid | Varies | Futures, options data | Not implemented |

---

## 10. Regulatory & Compliance APIs

| Provider | Tier | Cost | Features | Implementation |
|----------|------|------|----------|----------------|
| **SEC EDGAR** | Free | $0 | All SEC filings | `@/src/backend/app/regulatory_compliance/sec_filing_analyzer.py` |
| **FINRA BrokerCheck** | Free | $0 | Broker-dealer info | Not implemented |
| **OFAC Sanctions** | Free | $0 | SDN list screening | Not implemented |
| **OpenSanctions** | Free | $0 | Global sanctions data | Not implemented |
| **ComplyAdvantage** | Paid | $$ | AML screening | Not implemented |
| **Refinitiv World-Check** | Paid | $$$ | Risk screening | Not implemented |

---

## 11. Implementation Status

### 11.1 Fully Implemented

- ✅ Polygon.io (Market Data)
- ✅ Alpaca (Trading + Data)
- ✅ Interactive Brokers (Multi-asset Trading)
- ✅ Trading212 (CFD/Stock Trading)
- ✅ Coinbase Pro (Crypto)
- ✅ Binance (Crypto)
- ✅ Plaid (Bank Sync)
- ✅ Ollama (Local LLM)
- ✅ Groq (Cloud LLM)
- ✅ ESG Providers (MSCI, Sustainalytics framework)
- ✅ Metals Tracker (GoldAPI)
- ✅ Fiat Exchanges (Wise, OANDA)

### 11.2 Partially Implemented

- ⚠️ Alpha Vantage (Config only)
- ⚠️ Twitter/X API (Basic structure)
- ⚠️ Reddit API (Basic structure)
- ⚠️ SEC EDGAR (Form 4 only)

### 11.3 Not Yet Implemented

- ❌ IEX Cloud
- ❌ Twelve Data
- ❌ CoinGecko / CoinMarketCap (Crypto data only)
- ❌ NewsAPI (Full integration)
- ❌ OpenAI/Anthropic (Fallback only)
- ❌ TrueLayer (EU banking)
- ❌ Fixer.io / Open Exchange Rates

---

## 12. API Key Management

### 12.1 Environment Variables

All API keys should be stored in environment variables:

```bash
# Market Data
POLYGON_API_KEY=your_polygon_key
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ALPHA_VANTAGE_KEY=your_av_key

# Trading
IBKR_ACCOUNT_ID=your_ibkr_account
TRADING212_API_KEY=your_t212_key
COINBASE_API_KEY=your_cb_key
COINBASE_SECRET=your_cb_secret
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET=your_binance_secret

# Banking
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENVIRONMENT=sandbox|development|production

# AI/LLM
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key

# Forex/Fiat
WISE_API_KEY=your_wise_key
OANDA_API_KEY=your_oanda_key
OANDA_ACCOUNT_ID=your_oanda_account

# Metals
GOLDAPI_KEY=your_goldapi_key
METALS_API_KEY=your_metals_key

# ESG
MSCI_API_KEY=your_msci_key
SUSTAINALYTICS_API_KEY=your_sustainalytics_key
REFINITIV_API_KEY=your_refinitiv_key

# News/Sentiment
NEWSAPI_KEY=your_newsapi_key
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
REDDIT_CLIENT_ID=your_reddit_client
REDDIT_SECRET=your_reddit_secret
```

### 12.2 Configuration File

See `@/src/backend/app/config.py` for centralized API configuration:

```python
from src.backend.app.config import Config

# Check if live data is configured
if Config.is_live_data_configured():
    print("Live data sources available")
    
# Get data source priority
priority = Config.get_data_source_priority()
# Returns: ['polygon', 'alpaca', 'yahoo', 'alpha_vantage', 'mock']

# Validate configuration
status = Config.validate()
print(status['valid'])  # True/False
print(status['warnings'])  # List of missing keys
```

---

## 13. Adding New APIs

### 13.1 Quick Start Template

When adding a new API integration, follow this structure:

```python
"""
[Provider Name] API Integration
=================================
Description of what this API does.

Free Tier: [Details]
Paid Tier: [Details]
"""

import os
import aiohttp
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class [Provider]Config:
    """Configuration for [Provider] API"""
    api_key: str
    base_url: str = "https://api.provider.com/v1"
    tier: str = "free"  # free, paid, enterprise
    
    def __post_init__(self):
        if not self.api_key:
            raise ValueError("API key required")

class [Provider]Client:
    """Client for [Provider] API"""
    
    def __init__(self, config: Optional[[Provider]Config] = None):
        self.config = config or [Provider]Config(
            api_key=os.getenv("[PROVIDER]_API_KEY")
        )
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_data(self, symbol: str) -> Dict:
        """Fetch data from API"""
        if not self.session:
            raise RuntimeError("Use async context manager")
        
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        url = f"{self.config.base_url}/data/{symbol}"
        
        async with self.session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 429:
                raise RateLimitError("API rate limit exceeded")
            else:
                raise APIError(f"API error: {resp.status}")

class RateLimitError(Exception):
    pass

class APIError(Exception):
    pass

# Usage
async with [Provider]Client() as client:
    data = await client.get_data("AAPL")
```

### 13.2 Registration Checklist

When adding a new API:

- [ ] Create client class in appropriate directory
- [ ] Add environment variable to `.env.example`
- [ ] Add configuration to `config.py`
- [ ] Document free/paid tier details in this catalog
- [ ] Add rate limiting handling
- [ ] Add error handling for common errors
- [ ] Create integration tests
- [ ] Update API_INTEGRATION_CATALOG.md

---

## 14. Rate Limiting Best Practices

### 14.1 Built-in Rate Limiters

```python
from src.backend.app.api_integration.live_data_manager import RateLimiter

# Create rate limiter: 100 requests per minute
limiter = RateLimiter(requests_per_minute=100)

# Use with context manager
async with limiter:
    data = await api_client.get_data("AAPL")
```

### 14.2 Exponential Backoff

```python
import asyncio
from random import uniform

async def fetch_with_retry(client, symbol, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.get_data(symbol)
        except RateLimitError:
            wait = (2 ** attempt) + uniform(0, 1)
            await asyncio.sleep(wait)
    raise Exception("Max retries exceeded")
```

---

## 15. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-03 | Initial catalog creation |

---

**Last Updated:** May 3, 2026  
**Maintained by:** Financial Master Development Team  
**Questions?** See `@/docs/api/API_SETUP_GUIDE.md` for setup instructions.
