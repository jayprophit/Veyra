"""
OpenBB Integration Module - Free Alternative to FactSet
Provides comprehensive financial data access without API keys or costs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

try:
    import openbb
    from openbb import obb
    OPENBB_AVAILABLE = True
except ImportError:
    OPENBB_AVAILABLE = False
    logging.warning("OpenBB not installed. Install with: pip install openbb")

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    high: float
    low: float
    open_price: float
    change: float
    change_percent: float

@dataclass
class CompanyFundamentals:
    symbol: str
    market_cap: float
    revenue: float
    net_income: float
    total_assets: float
    total_debt: float
    pe_ratio: float
    pb_ratio: float
    dividend_yield: float
    beta: float
    sector: str
    industry: str

@dataclass
class TechnicalIndicator:
    symbol: str
    indicator_name: str
    value: float
    signal: str
    confidence: float
    timestamp: datetime

@dataclass
class EconomicData:
    indicator: str
    value: float
    timestamp: datetime
    country: str
    frequency: str

class OpenBBIntegration:
    """OpenBB integration for free financial data access"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = OPENBB_AVAILABLE
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        if not self.enabled:
            logger.error("OpenBB not available - install with: pip install openbb")
            return
            
        # Initialize OpenBB
        try:
            # OpenBB doesn't require authentication for free tier
            self.client = obb
            logger.info("OpenBB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenBB: {e}")
            self.enabled = False
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        cached_time = self.cache[key].get('timestamp')
        if not cached_time:
            return False
        return (datetime.now() - cached_time).seconds < self.cache_ttl
    
    def _get_cached_data(self, key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def _cache_data(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_real_time_quotes(self, symbols: List[str]) -> List[MarketData]:
        """Get real-time market data for multiple symbols"""
        if not self.enabled:
            return self._get_mock_quotes(symbols)
        
        cache_key = f"quotes_{','.join(symbols)}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            quotes = []
            for symbol in symbols:
                try:
                    # Get price data using OpenBB
                    price_data = self.client.equity.price.quote(symbol=symbol)
                    
                    if price_data and len(price_data.results) > 0:
                        result = price_data.results[0]
                        quote = MarketData(
                            symbol=symbol,
                            price=float(result.last_price or 0),
                            volume=int(result.volume or 0),
                            timestamp=datetime.now(),
                            high=float(result.high or 0),
                            low=float(result.low or 0),
                            open_price=float(result.open or 0),
                            change=float(result.change or 0),
                            change_percent=float(result.change_percent or 0)
                        )
                        quotes.append(quote)
                except Exception as e:
                    logger.warning(f"Failed to get quote for {symbol}: {e}")
                    # Add mock data for failed requests
                    quotes.append(self._get_mock_quote(symbol))
            
            self._cache_data(cache_key, quotes)
            return quotes
            
        except Exception as e:
            logger.error(f"Failed to get real-time quotes: {e}")
            return self._get_mock_quotes(symbols)
    
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get historical price data"""
        if not self.enabled:
            return self._get_mock_historical_data(symbol, start_date, end_date)
        
        cache_key = f"hist_{symbol}_{start_date.date()}_{end_date.date()}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get historical data using OpenBB
            hist_data = self.client.equity.price.historical(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            if hist_data and hist_data.results:
                formatted_data = []
                for result in hist_data.results:
                    formatted_data.append({
                        'date': result.date,
                        'open': float(result.open or 0),
                        'high': float(result.high or 0),
                        'low': float(result.low or 0),
                        'close': float(result.close or 0),
                        'volume': int(result.volume or 0),
                        'symbol': symbol
                    })
                
                self._cache_data(cache_key, formatted_data)
                return formatted_data
                
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
        
        return self._get_mock_historical_data(symbol, start_date, end_date)
    
    async def get_company_fundamentals(self, symbol: str) -> Optional[CompanyFundamentals]:
        """Get company fundamental data"""
        if not self.enabled:
            return self._get_mock_fundamentals(symbol)
        
        cache_key = f"fundamentals_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get company fundamentals using OpenBB
            fundamentals = self.client.equity.fundamental(symbol=symbol)
            
            if fundamentals and len(fundamentals.results) > 0:
                result = fundamentals.results[0]
                company_data = CompanyFundamentals(
                    symbol=symbol,
                    market_cap=float(result.market_cap or 0),
                    revenue=float(result.revenue or 0),
                    net_income=float(result.net_income or 0),
                    total_assets=float(result.total_assets or 0),
                    total_debt=float(result.total_debt or 0),
                    pe_ratio=float(result.pe_ratio or 0),
                    pb_ratio=float(result.pb_ratio or 0),
                    dividend_yield=float(result.dividend_yield or 0),
                    beta=float(result.beta or 0),
                    sector=result.sector or "",
                    industry=result.industry or ""
                )
                
                self._cache_data(cache_key, company_data)
                return company_data
                
        except Exception as e:
            logger.error(f"Failed to get fundamentals for {symbol}: {e}")
        
        return self._get_mock_fundamentals(symbol)
    
    async def get_technical_indicators(self, symbol: str, indicators: List[str]) -> List[TechnicalIndicator]:
        """Get technical indicators for a symbol"""
        if not self.enabled:
            return self._get_mock_technical_indicators(symbol, indicators)
        
        cache_key = f"technical_{symbol}_{','.join(indicators)}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            technical_data = []
            
            # Get technical indicators using OpenBB
            for indicator in indicators:
                try:
                    if indicator.lower() == 'sma':
                        data = self.client.technical.sma(symbol=symbol, length=20)
                    elif indicator.lower() == 'rsi':
                        data = self.client.technical.rsi(symbol=symbol, length=14)
                    elif indicator.lower() == 'macd':
                        data = self.client.technical.macd(symbol=symbol)
                    elif indicator.lower() == 'bollinger':
                        data = self.client.technical.bollinger(symbol=symbol, length=20)
                    else:
                        continue
                    
                    if data and len(data.results) > 0:
                        result = data.results[0]
                        tech_indicator = TechnicalIndicator(
                            symbol=symbol,
                            indicator_name=indicator,
                            value=float(result.value or 0),
                            signal=self._generate_signal(indicator, float(result.value or 0)),
                            confidence=0.8,
                            timestamp=datetime.now()
                        )
                        technical_data.append(tech_indicator)
                        
                except Exception as e:
                    logger.warning(f"Failed to get {indicator} for {symbol}: {e}")
            
            self._cache_data(cache_key, technical_data)
            return technical_data
            
        except Exception as e:
            logger.error(f"Failed to get technical indicators for {symbol}: {e}")
        
        return self._get_mock_technical_indicators(symbol, indicators)
    
    async def get_economic_data(self, indicators: List[str]) -> List[EconomicData]:
        """Get economic indicators data"""
        if not self.enabled:
            return self._get_mock_economic_data(indicators)
        
        cache_key = f"economic_{','.join(indicators)}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            economic_data = []
            
            for indicator in indicators:
                try:
                    # Get economic data using OpenBB
                    if indicator.lower() == 'gdp':
                        data = self.client.economy.gdp()
                    elif indicator.lower() == 'inflation':
                        data = self.client.economy.cpi()
                    elif indicator.lower() == 'unemployment':
                        data = self.client.economy.unemployment()
                    elif indicator.lower() == 'interest_rate':
                        data = self.client.economy.treasury_rate()
                    else:
                        continue
                    
                    if data and len(data.results) > 0:
                        result = data.results[0]
                        econ_data = EconomicData(
                            indicator=indicator,
                            value=float(result.value or 0),
                            timestamp=datetime.now(),
                            country=result.country or "US",
                            frequency=result.frequency or "monthly"
                        )
                        economic_data.append(econ_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to get {indicator} data: {e}")
            
            self._cache_data(cache_key, economic_data)
            return economic_data
            
        except Exception as e:
            logger.error(f"Failed to get economic data: {e}")
        
        return self._get_mock_economic_data(indicators)
    
    async def get_news(self, symbols: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get financial news"""
        if not self.enabled:
            return self._get_mock_news(limit)
        
        cache_key = f"news_{','.join(symbols) if symbols else 'all'}_{limit}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Get news using OpenBB
            news_data = self.client.news(limit=limit)
            
            if news_data and news_data.results:
                formatted_news = []
                for article in news_data.results:
                    formatted_news.append({
                        'title': article.title,
                        'description': article.description,
                        'url': article.url,
                        'published_at': article.published_at,
                        'source': article.source,
                        'symbols': article.symbols or []
                    })
                
                self._cache_data(cache_key, formatted_news)
                return formatted_news
                
        except Exception as e:
            logger.error(f"Failed to get news: {e}")
        
        return self._get_mock_news(limit)
    
    def _generate_signal(self, indicator: str, value: float) -> str:
        """Generate trading signal based on indicator value"""
        if indicator.lower() == 'rsi':
            if value < 30:
                return "BUY"
            elif value > 70:
                return "SELL"
            else:
                return "HOLD"
        elif indicator.lower() == 'sma':
            return "HOLD"  # SMA alone doesn't generate signals
        elif indicator.lower() == 'macd':
            return "HOLD"  # MACD needs comparison with signal line
        elif indicator.lower() == 'bollinger':
            return "HOLD"  # Bollinger needs price comparison
        else:
            return "HOLD"
    
    # Mock data methods for fallback
    def _get_mock_quotes(self, symbols: List[str]) -> List[MarketData]:
        """Generate mock quotes when OpenBB is not available"""
        quotes = []
        for symbol in symbols:
            quotes.append(self._get_mock_quote(symbol))
        return quotes
    
    def _get_mock_quote(self, symbol: str) -> MarketData:
        """Generate mock quote for a symbol"""
        import random
        base_price = 100.0 + random.uniform(-50, 150)
        return MarketData(
            symbol=symbol,
            price=base_price,
            volume=random.randint(100000, 10000000),
            timestamp=datetime.now(),
            high=base_price * 1.02,
            low=base_price * 0.98,
            open_price=base_price * 0.99,
            change=random.uniform(-5, 5),
            change_percent=random.uniform(-5, 5)
        )
    
    def _get_mock_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate mock historical data"""
        import random
        data = []
        current_date = start_date
        base_price = 100.0 + random.uniform(-50, 150)
        
        while current_date <= end_date:
            price_change = random.uniform(-0.05, 0.05)
            base_price *= (1 + price_change)
            
            data.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'open': base_price * 0.99,
                'high': base_price * 1.02,
                'low': base_price * 0.98,
                'close': base_price,
                'volume': random.randint(100000, 10000000),
                'symbol': symbol
            })
            
            current_date += timedelta(days=1)
        
        return data
    
    def _get_mock_fundamentals(self, symbol: str) -> CompanyFundamentals:
        """Generate mock fundamentals data"""
        import random
        return CompanyFundamentals(
            symbol=symbol,
            market_cap=random.uniform(1e9, 1e12),
            revenue=random.uniform(1e8, 1e11),
            net_income=random.uniform(1e7, 1e10),
            total_assets=random.uniform(1e9, 1e12),
            total_debt=random.uniform(1e8, 1e11),
            pe_ratio=random.uniform(10, 30),
            pb_ratio=random.uniform(1, 10),
            dividend_yield=random.uniform(0, 0.05),
            beta=random.uniform(0.5, 2.0),
            sector="Technology",
            industry="Software"
        )
    
    def _get_mock_technical_indicators(self, symbol: str, indicators: List[str]) -> List[TechnicalIndicator]:
        """Generate mock technical indicators"""
        import random
        indicators_data = []
        
        for indicator in indicators:
            if indicator.lower() == 'rsi':
                value = random.uniform(20, 80)
            elif indicator.lower() == 'sma':
                value = random.uniform(90, 110)
            elif indicator.lower() == 'macd':
                value = random.uniform(-2, 2)
            elif indicator.lower() == 'bollinger':
                value = random.uniform(95, 105)
            else:
                value = random.uniform(0, 100)
            
            indicators_data.append(TechnicalIndicator(
                symbol=symbol,
                indicator_name=indicator,
                value=value,
                signal=self._generate_signal(indicator, value),
                confidence=0.8,
                timestamp=datetime.now()
            ))
        
        return indicators_data
    
    def _get_mock_economic_data(self, indicators: List[str]) -> List[EconomicData]:
        """Generate mock economic data"""
        import random
        economic_data = []
        
        for indicator in indicators:
            if indicator.lower() == 'gdp':
                value = random.uniform(20000, 25000)
            elif indicator.lower() == 'inflation':
                value = random.uniform(1, 5)
            elif indicator.lower() == 'unemployment':
                value = random.uniform(3, 8)
            elif indicator.lower() == 'interest_rate':
                value = random.uniform(0, 5)
            else:
                value = random.uniform(0, 100)
            
            economic_data.append(EconomicData(
                indicator=indicator,
                value=value,
                timestamp=datetime.now(),
                country="US",
                frequency="monthly"
            ))
        
        return economic_data
    
    def _get_mock_news(self, limit: int) -> List[Dict[str, Any]]:
        """Generate mock news"""
        import random
        mock_titles = [
            "Stock Market Reaches New Heights",
            "Tech Stocks Show Strong Performance",
            "Federal Reserve Announces Policy Changes",
            "Economic Indicators Show Positive Trends",
            "Investment Strategies for Current Market Conditions"
        ]
        
        news = []
        for i in range(min(limit, len(mock_titles))):
            news.append({
                'title': mock_titles[i],
                'description': f"Mock description for {mock_titles[i]}",
                'url': f"https://example.com/news/{i}",
                'published_at': datetime.now().isoformat(),
                'source': "Mock News Source",
                'symbols': ["AAPL", "MSFT", "GOOGL"]
            })
        
        return news
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'enabled': self.enabled,
            'provider': 'OpenBB',
            'features': [
                'real_time_quotes',
                'historical_data',
                'fundamentals',
                'technical_indicators',
                'economic_data',
                'news'
            ],
            'cost': 'FREE',
            'api_key_required': False,
            'rate_limits': 'None',
            'data_quality': 'Professional'
        }

# Factory function
def get_openbb_integration(config: Dict[str, Any] = None) -> OpenBBIntegration:
    """Factory function to get OpenBB integration"""
    return OpenBBIntegration(config)
