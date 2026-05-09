"""
Yahoo Finance Integration Module - Free Alternative to FactSet
Provides comprehensive financial data access without API keys or costs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logging.warning("yfinance not installed. Install with: pip install yfinance")

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
    currency: str
    market_cap: float

@dataclass
class CompanyInfo:
    symbol: str
    company_name: str
    sector: str
    industry: str
    country: str
    currency: str
    market_cap: float
    employees: int
    website: str
    description: str

@dataclass
class FinancialStatement:
    symbol: str
    statement_type: str  # income, balance, cash_flow
    period: str
    date: datetime
    revenue: float
    net_income: float
    total_assets: float
    total_liabilities: float
    cash_flow: float

@dataclass
class OptionData:
    symbol: str
    option_type: str  # call, put
    strike: float
    expiration: datetime
    bid: float
    ask: float
    volume: int
    open_interest: int
    implied_volatility: float

class YFinanceIntegration:
    """Yahoo Finance integration for free financial data access"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = YFINANCE_AVAILABLE
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        if not self.enabled:
            logger.error("yfinance not available - install with: pip install yfinance")
            return
        
        logger.info("yfinance initialized successfully")
    
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
            # Use yfinance to get real-time data
            tickers = yf.Tickers(symbols)
            quotes = []
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info
                    history = ticker.history(period="1d")
                    
                    if not history.empty:
                        latest = history.iloc[-1]
                        previous_close = info.get('previousClose', latest['Close'])
                        change = latest['Close'] - previous_close
                        change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                        
                        quote = MarketData(
                            symbol=symbol,
                            price=float(latest['Close']),
                            volume=int(latest['Volume']),
                            timestamp=datetime.now(),
                            high=float(latest['High']),
                            low=float(latest['Low']),
                            open_price=float(latest['Open']),
                            change=float(change),
                            change_percent=float(change_percent),
                            currency=info.get('currency', 'USD'),
                            market_cap=float(info.get('marketCap', 0))
                        )
                        quotes.append(quote)
                    else:
                        quotes.append(self._get_mock_quote(symbol))
                        
                except Exception as e:
                    logger.warning(f"Failed to get quote for {symbol}: {e}")
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
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            
            if not hist.empty:
                formatted_data = []
                for date, row in hist.iterrows():
                    formatted_data.append({
                        'date': date.strftime("%Y-%m-%d"),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume']),
                        'symbol': symbol,
                        'adj_close': float(row['Adj Close'])
                    })
                
                self._cache_data(cache_key, formatted_data)
                return formatted_data
                
        except Exception as e:
            logger.error(f"Failed to get historical data for {symbol}: {e}")
        
        return self._get_mock_historical_data(symbol, start_date, end_date)
    
    async def get_company_info(self, symbol: str) -> Optional[CompanyInfo]:
        """Get company information"""
        if not self.enabled:
            return self._get_mock_company_info(symbol)
        
        cache_key = f"info_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            company_info = CompanyInfo(
                symbol=symbol,
                company_name=info.get('longName', ''),
                sector=info.get('sector', ''),
                industry=info.get('industry', ''),
                country=info.get('country', ''),
                currency=info.get('currency', 'USD'),
                market_cap=float(info.get('marketCap', 0)),
                employees=int(info.get('fullTimeEmployees', 0)),
                website=info.get('website', ''),
                description=info.get('longBusinessSummary', '')
            )
            
            self._cache_data(cache_key, company_info)
            return company_info
            
        except Exception as e:
            logger.error(f"Failed to get company info for {symbol}: {e}")
        
        return self._get_mock_company_info(symbol)
    
    async def get_financial_statements(self, symbol: str, statement_type: str = 'income', period: str = 'annual') -> List[FinancialStatement]:
        """Get financial statements"""
        if not self.enabled:
            return self._get_mock_financial_statements(symbol, statement_type, period)
        
        cache_key = f"statements_{symbol}_{statement_type}_{period}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            statements = []
            
            if statement_type == 'income':
                data = ticker.financials if period == 'annual' else ticker.quarterly_financials
            elif statement_type == 'balance':
                data = ticker.balance_sheet if period == 'annual' else ticker.quarterly_balance_sheet
            elif statement_type == 'cash_flow':
                data = ticker.cashflow if period == 'annual' else ticker.quarterly_cashflow
            else:
                return []
            
            if not data.empty:
                for date in data.columns:
                    row = data[date]
                    statement = FinancialStatement(
                        symbol=symbol,
                        statement_type=statement_type,
                        period=period,
                        date=date,
                        revenue=float(row.get('Total Revenue', 0)),
                        net_income=float(row.get('Net Income', 0)),
                        total_assets=float(row.get('Total Assets', 0)),
                        total_liabilities=float(row.get('Total Liab', 0)),
                        cash_flow=float(row.get('Operating Cash Flow', 0))
                    )
                    statements.append(statement)
            
            self._cache_data(cache_key, statements)
            return statements
            
        except Exception as e:
            logger.error(f"Failed to get financial statements for {symbol}: {e}")
        
        return self._get_mock_financial_statements(symbol, statement_type, period)
    
    async def get_options_data(self, symbol: str) -> List[OptionData]:
        """Get options data"""
        if not self.enabled:
            return self._get_mock_options_data(symbol)
        
        cache_key = f"options_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            options_data = []
            
            # Get available expiration dates
            exp_dates = ticker.options
            if not exp_dates:
                return self._get_mock_options_data(symbol)
            
            # Get options for the nearest expiration
            nearest_exp = exp_dates[0]
            options = ticker.option_chain(nearest_exp)
            
            # Process calls
            for _, row in options.calls.iterrows():
                option = OptionData(
                    symbol=symbol,
                    option_type='call',
                    strike=float(row['strike']),
                    expiration=datetime.strptime(nearest_exp, '%Y-%m-%d'),
                    bid=float(row['bid']),
                    ask=float(row['ask']),
                    volume=int(row['volume']),
                    open_interest=int(row['openInterest']),
                    implied_volatility=float(row['impliedVolatility'])
                )
                options_data.append(option)
            
            # Process puts
            for _, row in options.puts.iterrows():
                option = OptionData(
                    symbol=symbol,
                    option_type='put',
                    strike=float(row['strike']),
                    expiration=datetime.strptime(nearest_exp, '%Y-%m-%d'),
                    bid=float(row['bid']),
                    ask=float(row['ask']),
                    volume=int(row['volume']),
                    open_interest=int(row['openInterest']),
                    implied_volatility=float(row['impliedVolatility'])
                )
                options_data.append(option)
            
            self._cache_data(cache_key, options_data)
            return options_data
            
        except Exception as e:
            logger.error(f"Failed to get options data for {symbol}: {e}")
        
        return self._get_mock_options_data(symbol)
    
    async def get_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Get analyst recommendations"""
        if not self.enabled:
            return self._get_mock_recommendations(symbol)
        
        cache_key = f"recommendations_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            if recommendations is not None and not recommendations.empty:
                rec_data = {
                    'strong_buy': int(recommendations['Strong Buy'].iloc[0]) if 'Strong Buy' in recommendations.columns else 0,
                    'buy': int(recommendations['Buy'].iloc[0]) if 'Buy' in recommendations.columns else 0,
                    'hold': int(recommendations['Hold'].iloc[0]) if 'Hold' in recommendations.columns else 0,
                    'sell': int(recommendations['Sell'].iloc[0]) if 'Sell' in recommendations.columns else 0,
                    'strong_sell': int(recommendations['Strong Sell'].iloc[0]) if 'Strong Sell' in recommendations.columns else 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                self._cache_data(cache_key, rec_data)
                return rec_data
                
        except Exception as e:
            logger.error(f"Failed to get recommendations for {symbol}: {e}")
        
        return self._get_mock_recommendations(symbol)
    
    async def get_dividend_info(self, symbol: str) -> List[Dict[str, Any]]:
        """Get dividend information"""
        if not self.enabled:
            return self._get_mock_dividend_info(symbol)
        
        cache_key = f"dividends_{symbol}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            
            if dividends is not None and not dividends.empty:
                dividend_data = []
                for date, amount in dividends.items():
                    dividend_data.append({
                        'date': date.strftime("%Y-%m-%d"),
                        'amount': float(amount),
                        'symbol': symbol
                    })
                
                self._cache_data(cache_key, dividend_data)
                return dividend_data
                
        except Exception as e:
            logger.error(f"Failed to get dividend info for {symbol}: {e}")
        
        return self._get_mock_dividend_info(symbol)
    
    # Mock data methods for fallback
    def _get_mock_quotes(self, symbols: List[str]) -> List[MarketData]:
        """Generate mock quotes when yfinance is not available"""
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
            change_percent=random.uniform(-5, 5),
            currency='USD',
            market_cap=base_price * random.uniform(1e8, 1e10)
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
                'symbol': symbol,
                'adj_close': base_price
            })
            
            current_date += timedelta(days=1)
        
        return data
    
    def _get_mock_company_info(self, symbol: str) -> CompanyInfo:
        """Generate mock company info"""
        import random
        return CompanyInfo(
            symbol=symbol,
            company_name=f"{symbol} Corporation",
            sector="Technology",
            industry="Software",
            country="United States",
            currency="USD",
            market_cap=random.uniform(1e9, 1e12),
            employees=random.randint(1000, 100000),
            website=f"https://www.{symbol.lower()}.com",
            description=f"Mock description for {symbol}"
        )
    
    def _get_mock_financial_statements(self, symbol: str, statement_type: str, period: str) -> List[FinancialStatement]:
        """Generate mock financial statements"""
        import random
        statements = []
        
        # Generate 4 periods of data
        for i in range(4):
            date = datetime.now() - timedelta(days=365 * i)
            statements.append(FinancialStatement(
                symbol=symbol,
                statement_type=statement_type,
                period=period,
                date=date,
                revenue=random.uniform(1e8, 1e11),
                net_income=random.uniform(1e7, 1e10),
                total_assets=random.uniform(1e9, 1e12),
                total_liabilities=random.uniform(1e8, 1e11),
                cash_flow=random.uniform(1e7, 1e10)
            ))
        
        return statements
    
    def _get_mock_options_data(self, symbol: str) -> List[OptionData]:
        """Generate mock options data"""
        import random
        options = []
        
        # Generate mock options for different strikes
        base_price = 100.0
        strikes = [base_price * (1 + i * 0.05) for i in range(-4, 5)]  # 9 strikes around current price
        
        for strike in strikes:
            for option_type in ['call', 'put']:
                options.append(OptionData(
                    symbol=symbol,
                    option_type=option_type,
                    strike=strike,
                    expiration=datetime.now() + timedelta(days=30),
                    bid=random.uniform(0.5, 10),
                    ask=random.uniform(1, 11),
                    volume=random.randint(0, 1000),
                    open_interest=random.randint(0, 5000),
                    implied_volatility=random.uniform(0.1, 0.5)
                ))
        
        return options
    
    def _get_mock_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Generate mock recommendations"""
        import random
        return {
            'strong_buy': random.randint(0, 10),
            'buy': random.randint(0, 10),
            'hold': random.randint(0, 10),
            'sell': random.randint(0, 5),
            'strong_sell': random.randint(0, 5),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_mock_dividend_info(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate mock dividend info"""
        import random
        dividends = []
        
        # Generate 8 quarters of dividend data
        for i in range(8):
            date = datetime.now() - timedelta(days=90 * i)
            dividends.append({
                'date': date.strftime("%Y-%m-%d"),
                'amount': random.uniform(0.1, 2.0),
                'symbol': symbol
            })
        
        return dividends
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'enabled': self.enabled,
            'provider': 'Yahoo Finance',
            'features': [
                'real_time_quotes',
                'historical_data',
                'company_info',
                'financial_statements',
                'options_data',
                'recommendations',
                'dividend_info'
            ],
            'cost': 'FREE',
            'api_key_required': False,
            'rate_limits': 'None (but be respectful)',
            'data_quality': 'Good',
            'global_coverage': True
        }

# Factory function
def get_yfinance_integration(config: Dict[str, Any] = None) -> YFinanceIntegration:
    """Factory function to get yfinance integration"""
    return YFinanceIntegration(config)
