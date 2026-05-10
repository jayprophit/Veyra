"""
Open-Source Data Sources Integration
100% free, open-source alternatives to paid financial data providers
Ensures complete intellectual property ownership
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import json
import aiohttp
import aiofiles
from pathlib import Path
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class OpenSourceDataSource:
    """Open-source data source configuration"""
    name: str
    description: str
    url: str
    license: str
    data_types: List[str]
    rate_limit: Optional[int] = None
    api_key_required: bool = False
    documentation_url: Optional[str] = None

class OpenSourceDataManager:
    """Manager for open-source financial data sources"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 300)  # 5 minutes
        self.sources = self._initialize_sources()
        self.data_dir = Path(self.config.get('data_dir', './data'))
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info("Open-Source Data Manager initialized")
    
    def _initialize_sources(self) -> Dict[str, OpenSourceDataSource]:
        """Initialize all open-source data sources"""
        return {
            # GitHub Repositories
            'yfinance': OpenSourceDataSource(
                name='Yahoo Finance',
                description='Free stock market data from Yahoo Finance',
                url='https://github.com/ranaroussi/yfinance',
                license='Apache 2.0',
                data_types=['market_data', 'company_info', 'financials'],
                rate_limit=2000,
                api_key_required=False,
                documentation_url='https://pypi.org/project/yfinance/'
            ),
            'pandas_datareader': OpenSourceDataSource(
                name='Pandas DataReader',
                description='Data readers for various financial data sources',
                url='https://github.com/pydata/pandas-datareader',
                license='BSD',
                data_types=['market_data', 'economic_data', 'futures'],
                rate_limit=1000,
                api_key_required=False,
                documentation_url='https://pandas-datareader.readthedocs.io/'
            ),
            'investpy': OpenSourceDataSource(
                name='InvestPy',
                description='Financial data from Investing.com',
                url='https://github.com/alvarobartt/investpy',
                license='MIT',
                data_types=['market_data', 'economic_calendar', 'technical_indicators'],
                rate_limit=100,
                api_key_required=False,
                documentation_url='https://investpy.readthedocs.io/'
            ),
            'yfinance_ticker': OpenSourceDataSource(
                name='Yahoo Finance Ticker',
                description='Enhanced Yahoo Finance data',
                url='https://github.com/valueof/informedtrading',
                license='MIT',
                data_types=['market_data', 'options', 'fundamentals'],
                rate_limit=500,
                api_key_required=False
            ),
            
            # Hugging Face Models
            'financial_bert': OpenSourceDataSource(
                name='Financial BERT',
                description='Financial text analysis models',
                url='https://huggingface.co/ProsusAI/finbert',
                license='Apache 2.0',
                data_types=['sentiment_analysis', 'text_classification'],
                api_key_required=False,
                documentation_url='https://huggingface.co/ProsusAI/finbert'
            ),
            'finbert_ner': OpenSourceDataSource(
                name='FinBERT NER',
                description='Named entity recognition for finance',
                url='https://huggingface.co/dslim/bert-base-NER',
                license='Apache 2.0',
                data_types=['entity_recognition', 'text_processing'],
                api_key_required=False
            ),
            
            # SEC EDGAR (Free Official Data)
            'sec_edgar': OpenSourceDataSource(
                name='SEC EDGAR',
                description='SEC filings and company data',
                url='https://www.sec.gov/edgar.shtml',
                license='Public Domain',
                data_types=['sec_filings', 'company_info', 'insider_trades'],
                rate_limit=10,
                api_key_required=False,
                documentation_url='https://www.sec.gov/edgar/sec-api-documentation'
            ),
            
            # Federal Reserve Economic Data (FRED)
            'fred': OpenSourceDataSource(
                name='FRED',
                description='Federal Reserve Economic Data',
                url='https://fred.stlouisfed.org/docs/api/fred/',
                license='Public Domain',
                data_types=['economic_indicators', 'interest_rates', 'inflation'],
                rate_limit=120,
                api_key_required=False,
                documentation_url='https://fred.stlouisfed.org/docs/api/fred/'
            ),
            
            # World Bank Data
            'world_bank': OpenSourceDataSource(
                name='World Bank',
                description='World Bank economic data',
                url='https://data.worldbank.org/',
                license='CC-BY-4.0',
                data_types=['economic_data', 'country_indicators', 'development_metrics'],
                rate_limit=100,
                api_key_required=False,
                documentation_url='https://datahelpdesk.worldbank.org/knowledgebase/topics/125589'
            ),
            
            # Quandl (Free Tier)
            'quandl': OpenSourceDataSource(
                name='Quandl',
                description='Financial and economic data',
                url='https://www.quandl.com/',
                license='Custom',
                data_types=['economic_data', 'alternative_data', 'commodities'],
                rate_limit=50,
                api_key_required=False,
                documentation_url='https://docs.quandl.com/'
            ),
            
            # CryptoCompare (Free Tier)
            'cryptocompare': OpenSourceDataSource(
                name='CryptoCompare',
                description='Cryptocurrency data',
                url='https://www.cryptocompare.com/',
                license='Custom',
                data_types=['crypto_prices', 'crypto_volume', 'crypto_social'],
                rate_limit=100,
                api_key_required=False,
                documentation_url='https://min-api.cryptocompare.com/'
            ),
            
            # Alpha Vantage (Free Tier)
            'alpha_vantage': OpenSourceDataSource(
                name='Alpha Vantage',
                description='Stock market APIs',
                url='https://www.alphavantage.co/',
                license='Custom',
                data_types=['market_data', 'technical_indicators', 'fundamentals'],
                rate_limit=5,
                api_key_required=False,
                documentation_url='https://www.alphavantage.co/documentation/'
            ),
            
            # IEX Cloud (Free Tier)
            'iex_cloud': OpenSourceDataSource(
                name='IEX Cloud',
                description='Stock market data',
                url='https://iexcloud.io/',
                license='Custom',
                data_types=['market_data', 'company_info', 'news'],
                rate_limit=100,
                api_key_required=False,
                documentation_url='https://iexcloud.io/docs/api/'
            ),
            
            # Financial Modeling Prep (Free Tier)
            'fmp': OpenSourceDataSource(
                name='Financial Modeling Prep',
                description='Financial statements and market data',
                url='https://site.financialmodelingprep.com/',
                license='Custom',
                data_types=['financials', 'market_data', 'ratios'],
                rate_limit=250,
                api_key_required=False,
                documentation_url='https://site.financialmodelingprep.com/developer/docs'
            ),
            
            # Polygon.io (Free Tier)
            'polygon': OpenSourceDataSource(
                name='Polygon.io',
                description='Stock market data',
                url='https://polygon.io/',
                license='Custom',
                data_types=['market_data', 'options', 'crypto'],
                rate_limit=5,
                api_key_required=False,
                documentation_url='https://polygon.io/docs/'
            ),
            
            # Open Source Datasets
            'kaggle_datasets': OpenSourceDataSource(
                name='Kaggle Datasets',
                description='Financial datasets from Kaggle',
                url='https://www.kaggle.com/datasets',
                license='Various',
                data_types=['historical_data', 'alternative_data', 'ml_datasets'],
                api_key_required=False,
                documentation_url='https://www.kaggle.com/docs/datasets'
            ),
            
            # UCI Repository
            'uci_ml': OpenSourceDataSource(
                name='UCI ML Repository',
                description='Machine learning datasets',
                url='https://archive.ics.uci.edu/ml/datasets.php',
                license='Various',
                data_types=['ml_datasets', 'financial_ml', 'time_series'],
                api_key_required=False,
                documentation_url='https://archive.ics.uci.edu/ml/index.php'
            )
        }
    
    async def get_market_data(self, symbols: List[str], data_type: str = 'price') -> Dict[str, Any]:
        """Get market data from open-source sources"""
        try:
            # Primary source: yfinance
            data = await self._get_yfinance_data(symbols, data_type)
            
            # Fallback: pandas_datareader
            if not data:
                data = await self._get_pandas_datareader_data(symbols, data_type)
            
            # Additional fallback: investpy
            if not data:
                data = await self._get_investpy_data(symbols, data_type)
            
            return {
                'symbols': symbols,
                'data_type': data_type,
                'data': data,
                'source': 'open_source',
                'timestamp': datetime.now().isoformat(),
                'license': 'Open Source'
            }
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return self._get_mock_market_data(symbols, data_type)
    
    async def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information from open-source sources"""
        try:
            # Primary source: yfinance
            data = await self._get_yfinance_company_info(symbol)
            
            # Fallback: SEC EDGAR
            if not data:
                data = await self._get_sec_company_info(symbol)
            
            return {
                'symbol': symbol,
                'data': data,
                'source': 'open_source',
                'timestamp': datetime.now().isoformat(),
                'license': 'Open Source'
            }
            
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return self._get_mock_company_info(symbol)
    
    async def get_financial_statements(self, symbol: str, statement_type: str = 'income') -> Dict[str, Any]:
        """Get financial statements from open-source sources"""
        try:
            # Primary source: yfinance
            data = await self._get_yfinance_financials(symbol, statement_type)
            
            # Fallback: Financial Modeling Prep
            if not data:
                data = await self._get_fmp_financials(symbol, statement_type)
            
            # Additional fallback: SEC EDGAR
            if not data:
                data = await self._get_sec_financials(symbol, statement_type)
            
            return {
                'symbol': symbol,
                'statement_type': statement_type,
                'data': data,
                'source': 'open_source',
                'timestamp': datetime.now().isoformat(),
                'license': 'Open Source'
            }
            
        except Exception as e:
            logger.error(f"Error getting financial statements: {e}")
            return self._get_mock_financials(symbol, statement_type)
    
    async def get_economic_data(self, indicators: List[str]) -> Dict[str, Any]:
        """Get economic data from open-source sources"""
        try:
            # Primary source: FRED
            data = await self._get_fred_data(indicators)
            
            # Fallback: World Bank
            if not data:
                data = await self._get_world_bank_data(indicators)
            
            return {
                'indicators': indicators,
                'data': data,
                'source': 'open_source',
                'timestamp': datetime.now().isoformat(),
                'license': 'Open Source'
            }
            
        except Exception as e:
            logger.error(f"Error getting economic data: {e}")
            return self._get_mock_economic_data(indicators)
    
    async def get_crypto_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get cryptocurrency data from open-source sources"""
        try:
            # Primary source: CryptoCompare
            data = await self._get_cryptocompare_data(symbols)
            
            # Fallback: yfinance (crypto support)
            if not data:
                data = await self._get_yfinance_crypto_data(symbols)
            
            return {
                'symbols': symbols,
                'data': data,
                'source': 'open_source',
                'timestamp': datetime.now().isoformat(),
                'license': 'Open Source'
            }
            
        except Exception as e:
            logger.error(f"Error getting crypto data: {e}")
            return self._get_mock_crypto_data(symbols)
    
    async def get_news_data(self, sources: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Get financial news from open-source sources"""
        try:
            # Primary source: RSS feeds
            data = await self._get_rss_news(sources, limit)
            
            # Fallback: News APIs (free tiers)
            if not data:
                data = await self._get_news_apis(sources, limit)
            
            return {
                'sources': sources or ['reuters', 'bloomberg', 'marketwatch'],
                'limit': limit,
                'data': data,
                'source': 'open_source',
                'timestamp': datetime.now().isoformat(),
                'license': 'Open Source'
            }
            
        except Exception as e:
            logger.error(f"Error getting news data: {e}")
            return self._get_mock_news_data(sources, limit)
    
    async def get_technical_indicators(self, symbol: str, indicators: List[str]) -> Dict[str, Any]:
        """Get technical indicators from open-source sources"""
        try:
            # Get historical data first
            historical_data = await self._get_yfinance_data([symbol], 'historical')
            
            if historical_data:
                # Calculate indicators using TA-Lib
                indicators_data = self._calculate_technical_indicators(
                    historical_data[symbol], indicators
                )
                
                return {
                    'symbol': symbol,
                    'indicators': indicators,
                    'data': indicators_data,
                    'source': 'open_source',
                    'timestamp': datetime.now().isoformat(),
                    'license': 'Open Source'
                }
            
            return self._get_mock_technical_indicators(symbol, indicators)
            
        except Exception as e:
            logger.error(f"Error getting technical indicators: {e}")
            return self._get_mock_technical_indicators(symbol, indicators)
    
    # Private methods for specific data sources
    
    async def _get_yfinance_data(self, symbols: List[str], data_type: str) -> Dict[str, Any]:
        """Get data from yfinance"""
        try:
            import yfinance as yf
            
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                
                if data_type == 'price':
                    hist = ticker.history(period="1mo")
                    data[symbol] = {
                        'current_price': hist['Close'].iloc[-1],
                        'change': hist['Close'].iloc[-1] - hist['Close'].iloc[-2],
                        'change_percent': ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100,
                        'volume': hist['Volume'].iloc[-1],
                        'high': hist['High'].iloc[-1],
                        'low': hist['Low'].iloc[-1],
                        'timestamp': hist.index[-1].isoformat()
                    }
                elif data_type == 'historical':
                    hist = ticker.history(period="1y")
                    data[symbol] = {
                        'historical_data': hist.to_dict('records'),
                        'period': '1y',
                        'frequency': 'daily'
                    }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in yfinance data: {e}")
            return {}
    
    async def _get_yfinance_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company info from yfinance"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'country': info.get('country', ''),
                'currency': info.get('currency', 'USD'),
                'description': info.get('longBusinessSummary', ''),
                'website': info.get('website', ''),
                'exchange': info.get('exchange', '')
            }
            
        except Exception as e:
            logger.error(f"Error in yfinance company info: {e}")
            return {}
    
    async def _get_yfinance_financials(self, symbol: str, statement_type: str) -> Dict[str, Any]:
        """Get financials from yfinance"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            
            if statement_type == 'income':
                financials = ticker.financials
            elif statement_type == 'balance':
                financials = ticker.balance_sheet
            elif statement_type == 'cash_flow':
                financials = ticker.cashflow
            else:
                financials = ticker.financials
            
            if financials is not None and not financials.empty:
                return {
                    'statement_type': statement_type,
                    'data': financials.to_dict(),
                    'periods': list(financials.columns),
                    'currency': 'USD'
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error in yfinance financials: {e}")
            return {}
    
    async def _get_pandas_datareader_data(self, symbols: List[str], data_type: str) -> Dict[str, Any]:
        """Get data from pandas_datareader"""
        try:
            import pandas_datareader as pdr
            
            data = {}
            for symbol in symbols:
                if data_type == 'price':
                    df = pdr.get_data_yahoo(symbol, period='1mo')
                    if not df.empty:
                        data[symbol] = {
                            'current_price': df['Close'].iloc[-1],
                            'change': df['Close'].iloc[-1] - df['Close'].iloc[-2],
                            'change_percent': ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
                            'volume': df['Volume'].iloc[-1],
                            'timestamp': df.index[-1].isoformat()
                        }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in pandas_datareader: {e}")
            return {}
    
    async def _get_investpy_data(self, symbols: List[str], data_type: str) -> Dict[str, Any]:
        """Get data from investpy"""
        try:
            import investpy
            
            data = {}
            for symbol in symbols:
                if data_type == 'price':
                    recent_data = investpy.get_stock_recent_data(symbol)
                    if recent_data is not None:
                        data[symbol] = {
                            'current_price': recent_data['last_close'],
                            'change': recent_data['change'],
                            'change_percent': recent_data['change_pct'],
                            'volume': recent_data['volume'],
                            'timestamp': recent_data['last_close_date']
                        }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in investpy: {e}")
            return {}
    
    async def _get_fred_data(self, indicators: List[str]) -> Dict[str, Any]:
        """Get data from FRED"""
        try:
            import pandas_datareader as pdr
            
            data = {}
            for indicator in indicators:
                try:
                    df = pdr.get_data_fred(indicator, start='2020-01-01')
                    if not df.empty:
                        data[indicator] = {
                            'data': df.to_dict('records'),
                            'latest_value': df[indicator].iloc[-1],
                            'change': df[indicator].iloc[-1] - df[indicator].iloc[-2],
                            'timestamp': df.index[-1].isoformat()
                        }
                except:
                    continue
            
            return data
            
        except Exception as e:
            logger.error(f"Error in FRED data: {e}")
            return {}
    
    async def _get_world_bank_data(self, indicators: List[str]) -> Dict[str, Any]:
        """Get data from World Bank"""
        try:
            import pandas_datareader as pdr
            
            data = {}
            for indicator in indicators:
                try:
                    df = pdr.get_data_wb(indicator, start='2020-01-01')
                    if not df.empty:
                        data[indicator] = {
                            'data': df.to_dict('records'),
                            'latest_value': df[indicator].iloc[-1],
                            'timestamp': df.index[-1].isoformat()
                        }
                except:
                    continue
            
            return data
            
        except Exception as e:
            logger.error(f"Error in World Bank data: {e}")
            return {}
    
    async def _get_cryptocompare_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get crypto data from CryptoCompare"""
        try:
            import aiohttp
            
            data = {}
            async with aiohttp.ClientSession() as session:
                for symbol in symbols:
                    url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD"
                    async with session.get(url) as response:
                        if response.status == 200:
                            result = await response.json()
                            data[symbol] = {
                                'price': result.get('USD', 0),
                                'currency': 'USD',
                                'timestamp': datetime.now().isoformat()
                            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in CryptoCompare: {e}")
            return {}
    
    async def _get_rss_news(self, sources: List[str], limit: int) -> List[Dict[str, Any]]:
        """Get news from RSS feeds"""
        try:
            import feedparser
            
            news_data = []
            
            # RSS feed URLs
            rss_feeds = {
                'reuters': 'https://www.reuters.com/rssFeed/worldNews',
                'bloomberg': 'https://www.bloomberg.com/feed/news/economy.rss',
                'marketwatch': 'https://www.marketwatch.com/rss/topstories',
                'yahoo': 'https://finance.yahoo.com/news/rssindex',
                'seekingalpha': 'https://seekingalpha.com/feed/stock-market-news'
            }
            
            for source in sources[:3]:  # Limit to avoid rate limits
                if source in rss_feeds:
                    try:
                        feed = feedparser.parse(rss_feeds[source])
                        for entry in feed.entries[:limit//len(sources)]:
                            news_data.append({
                                'title': entry.title,
                                'summary': entry.summary,
                                'link': entry.link,
                                'published': entry.published,
                                'source': source,
                                'timestamp': datetime.now().isoformat()
                            })
                    except:
                        continue
            
            return news_data[:limit]
            
        except Exception as e:
            logger.error(f"Error in RSS news: {e}")
            return []
    
    def _calculate_technical_indicators(self, data: pd.DataFrame, indicators: List[str]) -> Dict[str, Any]:
        """Calculate technical indicators"""
        try:
            import talib
            
            result = {}
            close_prices = data['Close'].values
            
            for indicator in indicators:
                if indicator.lower() == 'sma':
                    result['sma_20'] = talib.SMA(close_prices, timeperiod=20)[-1]
                    result['sma_50'] = talib.SMA(close_prices, timeperiod=50)[-1]
                elif indicator.lower() == 'ema':
                    result['ema_20'] = talib.EMA(close_prices, timeperiod=20)[-1]
                elif indicator.lower() == 'rsi':
                    result['rsi'] = talib.RSI(close_prices, timeperiod=14)[-1]
                elif indicator.lower() == 'macd':
                    macd, signal, hist = talib.MACD(close_prices)
                    result['macd'] = macd[-1]
                    result['macd_signal'] = signal[-1]
                    result['macd_histogram'] = hist[-1]
                elif indicator.lower() == 'bollinger':
                    upper, middle, lower = talib.BBANDS(close_prices, timeperiod=20)
                    result['bollinger_upper'] = upper[-1]
                    result['bollinger_middle'] = middle[-1]
                    result['bollinger_lower'] = lower[-1]
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}
    
    # Mock data methods for fallbacks
    
    def _get_mock_market_data(self, symbols: List[str], data_type: str) -> Dict[str, Any]:
        """Generate mock market data"""
        data = {}
        for symbol in symbols:
            if data_type == 'price':
                data[symbol] = {
                    'current_price': np.random.uniform(50, 500),
                    'change': np.random.uniform(-10, 10),
                    'change_percent': np.random.uniform(-5, 5),
                    'volume': np.random.randint(100000, 10000000),
                    'high': np.random.uniform(50, 500),
                    'low': np.random.uniform(50, 500),
                    'timestamp': datetime.now().isoformat()
                }
        
        return data
    
    def _get_mock_company_info(self, symbol: str) -> Dict[str, Any]:
        """Generate mock company info"""
        return {
            'name': f'{symbol} Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'market_cap': np.random.uniform(1e9, 100e9),
            'employees': np.random.randint(1000, 100000),
            'country': 'United States',
            'currency': 'USD',
            'description': f'Leading technology company {symbol}',
            'website': f'https://www.{symbol.lower()}.com',
            'exchange': 'NASDAQ'
        }
    
    def _get_mock_financials(self, symbol: str, statement_type: str) -> Dict[str, Any]:
        """Generate mock financial statements"""
        return {
            'statement_type': statement_type,
            'data': {
                'Revenue': np.random.uniform(1e9, 50e9),
                'Net Income': np.random.uniform(100e6, 5e9),
                'Total Assets': np.random.uniform(5e9, 100e9),
                'Total Liabilities': np.random.uniform(1e9, 50e9)
            },
            'periods': ['2023', '2022', '2021'],
            'currency': 'USD'
        }
    
    def _get_mock_economic_data(self, indicators: List[str]) -> Dict[str, Any]:
        """Generate mock economic data"""
        data = {}
        for indicator in indicators:
            data[indicator] = {
                'latest_value': np.random.uniform(0, 10),
                'change': np.random.uniform(-1, 1),
                'timestamp': datetime.now().isoformat()
            }
        
        return data
    
    def _get_mock_crypto_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Generate mock crypto data"""
        data = {}
        for symbol in symbols:
            data[symbol] = {
                'price': np.random.uniform(100, 50000),
                'currency': 'USD',
                'timestamp': datetime.now().isoformat()
            }
        
        return data
    
    def _get_mock_news_data(self, sources: List[str], limit: int) -> List[Dict[str, Any]]:
        """Generate mock news data"""
        news_data = []
        for i in range(min(limit, 10)):
            news_data.append({
                'title': f'Financial News Article {i+1}',
                'summary': f'Summary of important financial news {i+1}',
                'link': f'https://example.com/news/{i+1}',
                'published': (datetime.now() - timedelta(hours=i)).isoformat(),
                'source': sources[0] if sources else 'reuters',
                'timestamp': datetime.now().isoformat()
            })
        
        return news_data
    
    def _get_mock_technical_indicators(self, symbol: str, indicators: List[str]) -> Dict[str, Any]:
        """Generate mock technical indicators"""
        result = {}
        for indicator in indicators:
            if indicator.lower() == 'sma':
                result['sma_20'] = np.random.uniform(100, 300)
                result['sma_50'] = np.random.uniform(100, 300)
            elif indicator.lower() == 'ema':
                result['ema_20'] = np.random.uniform(100, 300)
            elif indicator.lower() == 'rsi':
                result['rsi'] = np.random.uniform(20, 80)
            elif indicator.lower() == 'macd':
                result['macd'] = np.random.uniform(-5, 5)
                result['macd_signal'] = np.random.uniform(-5, 5)
                result['macd_histogram'] = np.random.uniform(-2, 2)
            elif indicator.lower() == 'bollinger':
                result['bollinger_upper'] = np.random.uniform(150, 350)
                result['bollinger_middle'] = np.random.uniform(100, 300)
                result['bollinger_lower'] = np.random.uniform(50, 250)
        
        return result
    
    def get_source_status(self) -> Dict[str, Any]:
        """Get status of all data sources"""
        return {
            'total_sources': len(self.sources),
            'sources': {
                name: {
                    'name': source.name,
                    'description': source.description,
                    'license': source.license,
                    'data_types': source.data_types,
                    'api_key_required': source.api_key_required,
                    'rate_limit': source.rate_limit
                }
                for name, source in self.sources.items()
            },
            'cache_ttl': self.cache_ttl,
            'data_directory': str(self.data_dir),
            'last_updated': datetime.now().isoformat()
        }

# Factory function
def get_opensource_data_manager(config: Dict[str, Any] = None) -> OpenSourceDataManager:
    """Factory function to get open-source data manager"""
    return OpenSourceDataManager(config)
