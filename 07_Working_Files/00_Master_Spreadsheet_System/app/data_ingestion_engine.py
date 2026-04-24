"""
Financial Master Data Ingestion Engine
API integrations for live market data
Version: 1.0
"""

import requests
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import time
import os
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Data_Ingestion_Engine')


@dataclass
class PriceData:
    """Standardized price data structure"""
    timestamp: datetime
    price: float
    volume: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    asset: str = ""
    source: str = ""


class BaseAPIClient(ABC):
    """Abstract base class for API clients"""
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: float = 1.0):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
    
    def _rate_limited_request(self, url: str, params: Dict = None) -> Dict:
        """Make rate-limited API request"""
        # Enforce rate limit
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            self.last_request_time = time.time()
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}
    
    @abstractmethod
    def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for symbol"""
        pass
    
    @abstractmethod
    def get_historical(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data"""
        pass


class CoinGeckoClient(BaseAPIClient):
    """CoinGecko API for crypto prices (free tier)"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        super().__init__(rate_limit=1.2)  # Free tier: 10-30 calls/minute
    
    def get_price(self, symbol: str, vs_currency: str = "gbp") -> Optional[PriceData]:
        """Get current crypto price"""
        # Map common symbols to CoinGecko IDs
        id_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'ADA': 'cardano',
            'SOL': 'solana',
            'DOT': 'polkadot',
            'MATIC': 'matic-network'
        }
        
        coin_id = id_map.get(symbol.upper(), symbol.lower())
        
        url = f"{self.BASE_URL}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': vs_currency,
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        
        data = self._rate_limited_request(url, params)
        
        if coin_id in data:
            return PriceData(
                timestamp=datetime.now(),
                price=data[coin_id][vs_currency],
                volume=data[coin_id].get(f'{vs_currency}_24h_vol'),
                asset=symbol,
                source='coingecko'
            )
        return None
    
    def get_historical(self, symbol: str, vs_currency: str = "gbp", days: int = 30) -> pd.DataFrame:
        """Get historical OHLC data"""
        id_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'ADA': 'cardano',
            'SOL': 'solana'
        }
        
        coin_id = id_map.get(symbol.upper(), symbol.lower())
        
        url = f"{self.BASE_URL}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily'
        }
        
        data = self._rate_limited_request(url, params)
        
        if 'prices' not in data:
            return pd.DataFrame()
        
        # Parse price data
        prices = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        volumes = pd.DataFrame(data.get('total_volumes', []), columns=['timestamp', 'volume'])
        
        prices['timestamp'] = pd.to_datetime(prices['timestamp'], unit='ms')
        
        if not volumes.empty:
            volumes['timestamp'] = pd.to_datetime(volumes['timestamp'], unit='ms')
            df = prices.merge(volumes, on='timestamp')
        else:
            df = prices
            df['volume'] = 0
        
        df.set_index('timestamp', inplace=True)
        df['asset'] = symbol
        
        return df


class AlphaVantageClient(BaseAPIClient):
    """Alpha Vantage API for stocks/ETFs"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, rate_limit=12.0)  # 5 calls/minute free
    
    def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get current stock price"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        data = self._rate_limited_request(self.BASE_URL, params)
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            return PriceData(
                timestamp=datetime.now(),
                price=float(quote.get('05. price', 0)),
                volume=float(quote.get('06. volume', 0)),
                asset=symbol,
                source='alphavantage'
            )
        return None
    
    def get_historical(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical daily prices"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': self.api_key,
            'outputsize': 'compact'
        }
        
        data = self._rate_limited_request(self.BASE_URL, params)
        
        if 'Time Series (Daily)' not in data:
            return pd.DataFrame()
        
        # Parse time series
        ts_data = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(ts_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df = df.astype(float)
        df.rename(columns={'close': 'price'}, inplace=True)
        
        # Limit to requested days
        df = df.tail(days)
        df['asset'] = symbol
        
        return df


class YahooFinanceScraper(BaseAPIClient):
    """Yahoo Finance scraper (no API key required)"""
    
    def __init__(self):
        super().__init__(rate_limit=0.5)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price from Yahoo Finance"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                
                return PriceData(
                    timestamp=datetime.now(),
                    price=meta.get('regularMarketPrice', 0),
                    asset=symbol,
                    source='yahoo'
                )
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
        
        return None
    
    def get_historical(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical data from Yahoo Finance"""
        end = int(datetime.now().timestamp())
        start = int((datetime.now() - timedelta(days=days)).timestamp())
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            'period1': start,
            'period2': end,
            'interval': '1d'
        }
        
        try:
            response = self.session.get(url, headers=self.headers, params=params, timeout=30)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                prices = result['indicators']['quote'][0]
                
                df = pd.DataFrame({
                    'timestamp': pd.to_datetime(timestamps, unit='s'),
                    'open': prices.get('open', []),
                    'high': prices.get('high', []),
                    'low': prices.get('low', []),
                    'price': prices.get('close', []),
                    'volume': prices.get('volume', [])
                })
                
                df.set_index('timestamp', inplace=True)
                df['asset'] = symbol
                df = df.dropna()
                
                return df
        except Exception as e:
            logger.error(f"Yahoo Finance historical error: {e}")
        
        return pd.DataFrame()


class GoldPriceClient(BaseAPIClient):
    """Gold price API client"""
    
    def __init__(self):
        super().__init__(rate_limit=1.0)
    
    def get_price(self, metal: str = "XAU", currency: str = "GBP") -> Optional[PriceData]:
        """Get current gold/silver price"""
        # Using GoldAPI.io alternative or fallback calculation
        # Free alternative: use Yahoo Finance for GLD (gold ETF proxy)
        
        yahoo = YahooFinanceScraper()
        symbol = "GC=F" if metal == "XAU" else "SI=F"  # Gold/Silver futures
        
        return yahoo.get_price(symbol)


class DataAggregationEngine:
    """Central engine to aggregate data from all sources"""
    
    def __init__(self):
        self.clients = {
            'crypto': CoinGeckoClient(),
            'yahoo': YahooFinanceScraper(),
            'gold': GoldPriceClient()
        }
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def get_current_prices(self, assets: Dict[str, str]) -> Dict[str, Optional[PriceData]]:
        """
        Get current prices for multiple assets
        
        Args:
            assets: Dict of {asset_name: asset_symbol}
                   e.g., {'BTC': 'bitcoin', 'VWRP': 'VWRP.L'}
        
        Returns:
            Dict of {asset_name: PriceData}
        """
        results = {}
        
        for asset, symbol in assets.items():
            # Check cache
            cache_key = f"price_{asset}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_duration:
                    results[asset] = cached_data
                    continue
            
            # Determine asset type and fetch
            price_data = None
            
            if asset in ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'MATIC']:
                price_data = self.clients['crypto'].get_price(asset)
            elif asset in ['XAU', 'XAG']:  # Gold/Silver
                price_data = self.clients['gold'].get_price(asset)
            else:
                # Stocks/ETFs
                price_data = self.clients['yahoo'].get_price(symbol)
            
            if price_data:
                self.cache[cache_key] = (datetime.now(), price_data)
            
            results[asset] = price_data
        
        return results
    
    def get_historical_data(self, assets: Dict[str, str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """Get historical data for multiple assets"""
        results = {}
        
        for asset, symbol in assets.items():
            try:
                if asset in ['BTC', 'ETH', 'ADA', 'SOL']:
                    df = self.clients['crypto'].get_historical(asset, days=days)
                else:
                    df = self.clients['yahoo'].get_historical(symbol, days=days)
                
                if not df.empty:
                    results[asset] = df
            except Exception as e:
                logger.error(f"Failed to get historical data for {asset}: {e}")
        
        return results
    
    def get_portfolio_snapshot(self, 
                              holdings: Dict[str, float],
                              symbols: Dict[str, str]) -> Dict:
        """Get complete portfolio snapshot with current values"""
        
        prices = self.get_current_prices(symbols)
        
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'holdings': {},
            'total_value_gbp': 0,
            'prices': {},
            'errors': []
        }
        
        for asset, units in holdings.items():
            price_data = prices.get(asset)
            
            if price_data:
                value = units * price_data.price
                snapshot['holdings'][asset] = {
                    'units': units,
                    'price_gbp': price_data.price,
                    'value_gbp': value,
                    'source': price_data.source
                }
                snapshot['total_value_gbp'] += value
                snapshot['prices'][asset] = price_data.price
            else:
                snapshot['errors'].append(f"Could not fetch price for {asset}")
        
        # Calculate allocations
        if snapshot['total_value_gbp'] > 0:
            for asset, data in snapshot['holdings'].items():
                data['allocation_pct'] = data['value_gbp'] / snapshot['total_value_gbp']
        
        return snapshot
    
    def update_spreadsheet_data(self, snapshot: Dict, output_path: str):
        """Export snapshot to CSV for spreadsheet import"""
        
        data = []
        for asset, holding in snapshot['holdings'].items():
            data.append({
                'asset': asset,
                'units': holding['units'],
                'price_gbp': holding['price_gbp'],
                'value_gbp': holding['value_gbp'],
                'allocation_pct': holding.get('allocation_pct', 0),
                'timestamp': snapshot['timestamp']
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        logger.info(f"Exported portfolio data to {output_path}")


# Example usage
def example_data_ingestion():
    """Demonstrate data ingestion capabilities"""
    
    engine = DataAggregationEngine()
    
    # Define assets
    assets = {
        'BTC': 'BTC',
        'ETH': 'ETH',
        'VWRP': 'VWRP.L',
        'GLD': 'GC=F'
    }
    
    print("\n=== Current Prices ===")
    prices = engine.get_current_prices(assets)
    for asset, price_data in prices.items():
        if price_data:
            print(f"{asset}: £{price_data.price:,.2f} (source: {price_data.source})")
        else:
            print(f"{asset}: Failed to fetch")
    
    # Portfolio snapshot
    print("\n=== Portfolio Snapshot ===")
    holdings = {
        'BTC': 0.0123,
        'ETH': 0.01,
        'VWRP': 0.5
    }
    
    snapshot = engine.get_portfolio_snapshot(holdings, assets)
    print(f"Total Value: £{snapshot['total_value_gbp']:,.2f}")
    
    for asset, data in snapshot['holdings'].items():
        print(f"{asset}: {data['units']} units @ £{data['price_gbp']:,.2f} = £{data['value_gbp']:,.2f} ({data.get('allocation_pct', 0):.1%})")
    
    # Export to CSV
    engine.update_spreadsheet_data(snapshot, 'portfolio_snapshot.csv')


if __name__ == "__main__":
    example_data_ingestion()
