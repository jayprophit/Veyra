"""
Free Data Sources Integration Module
Unified interface for all free financial data alternatives to FactSet
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json

from .openbb_integration import get_openbb_integration, OpenBBIntegration
from .yfinance_integration import get_yfinance_integration, YFinanceIntegration
from .edgar_integration import get_edgar_integration, EDGARIntegration
from .finance_toolkit_integration import get_finance_toolkit_integration, FinanceToolkitIntegration

logger = logging.getLogger(__name__)

@dataclass
class DataSourceStatus:
    name: str
    enabled: bool
    available: bool
    features: List[str]
    cost: str
    api_key_required: bool

@dataclass
class UnifiedMarketData:
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    source: str
    additional_data: Dict[str, Any]

@dataclass
class UnifiedCompanyData:
    symbol: str
    company_name: str
    sector: str
    industry: str
    market_cap: float
    fundamentals: Dict[str, Any]
    source: str

class FreeDataSourcesManager:
    """Unified manager for all free financial data sources"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sources = {}
        self.primary_source = None
        self.fallback_sources = []
        
        # Initialize all free data sources
        self._initialize_sources()
        
        # Set up source hierarchy
        self._setup_source_hierarchy()
        
        logger.info("Free Data Sources Manager initialized")
    
    def _initialize_sources(self):
        """Initialize all available free data sources"""
        
        # OpenBB Integration
        try:
            self.sources['openbb'] = get_openbb_integration(self.config.get('openbb', {}))
        except Exception as e:
            logger.error(f"Failed to initialize OpenBB: {e}")
            self.sources['openbb'] = None
        
        # Yahoo Finance Integration
        try:
            self.sources['yfinance'] = get_yfinance_integration(self.config.get('yfinance', {}))
        except Exception as e:
            logger.error(f"Failed to initialize yfinance: {e}")
            self.sources['yfinance'] = None
        
        # EDGAR Integration
        try:
            self.sources['edgar'] = get_edgar_integration(self.config.get('edgar', {}))
        except Exception as e:
            logger.error(f"Failed to initialize EDGAR: {e}")
            self.sources['edgar'] = None
        
        # Finance Toolkit Integration
        try:
            self.sources['finance_toolkit'] = get_finance_toolkit_integration(self.config.get('finance_toolkit', {}))
        except Exception as e:
            logger.error(f"Failed to initialize Finance Toolkit: {e}")
            self.sources['finance_toolkit'] = None
    
    def _setup_source_hierarchy(self):
        """Set up primary and fallback sources"""
        
        # Priority order for market data
        market_data_priority = ['openbb', 'yfinance']
        
        # Priority order for fundamentals
        fundamentals_priority = ['openbb', 'yfinance']
        
        # Priority order for SEC filings
        filings_priority = ['edgar']
        
        # Priority order for analysis
        analysis_priority = ['finance_toolkit', 'openbb']
        
        # Set primary source (first available in market data priority)
        for source_name in market_data_priority:
            source = self.sources.get(source_name)
            if source and source.enabled:
                self.primary_source = source_name
                break
        
        # Set fallback sources
        for source_name in market_data_priority:
            source = self.sources.get(source_name)
            if source and source.enabled and source_name != self.primary_source:
                self.fallback_sources.append(source_name)
        
        logger.info(f"Primary source: {self.primary_source}")
        logger.info(f"Fallback sources: {self.fallback_sources}")
    
    async def get_real_time_quotes(self, symbols: List[str]) -> List[UnifiedMarketData]:
        """Get real-time quotes with fallback support"""
        
        for source_name in [self.primary_source] + self.fallback_sources:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                quotes = await source.get_real_time_quotes(symbols)
                
                # Convert to unified format
                unified_quotes = []
                for quote in quotes:
                    unified_quote = UnifiedMarketData(
                        symbol=quote.symbol,
                        price=quote.price,
                        volume=quote.volume,
                        timestamp=quote.timestamp,
                        source=source_name,
                        additional_data={
                            'high': getattr(quote, 'high', None),
                            'low': getattr(quote, 'low', None),
                            'change': getattr(quote, 'change', None),
                            'change_percent': getattr(quote, 'change_percent', None)
                        }
                    )
                    unified_quotes.append(unified_quote)
                
                logger.info(f"Successfully got {len(unified_quotes)} quotes from {source_name}")
                return unified_quotes
                
            except Exception as e:
                logger.warning(f"Failed to get quotes from {source_name}: {e}")
                continue
        
        # If all sources fail, return mock data
        logger.error("All sources failed for real-time quotes, returning mock data")
        return self._get_mock_quotes(symbols)
    
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get historical data with fallback support"""
        
        for source_name in [self.primary_source] + self.fallback_sources:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                data = await source.get_historical_data(symbol, start_date, end_date)
                
                # Add source information
                for item in data:
                    item['source'] = source_name
                
                logger.info(f"Successfully got {len(data)} historical data points from {source_name}")
                return data
                
            except Exception as e:
                logger.warning(f"Failed to get historical data from {source_name}: {e}")
                continue
        
        logger.error("All sources failed for historical data, returning mock data")
        return self._get_mock_historical_data(symbol, start_date, end_date)
    
    async def get_company_data(self, symbol: str) -> Optional[UnifiedCompanyData]:
        """Get comprehensive company data"""
        
        for source_name in [self.primary_source] + self.fallback_sources:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                # Try to get company info
                if hasattr(source, 'get_company_info'):
                    company_info = await source.get_company_info(symbol)
                    
                    if company_info:
                        unified_data = UnifiedCompanyData(
                            symbol=symbol,
                            company_name=getattr(company_info, 'company_name', ''),
                            sector=getattr(company_info, 'sector', ''),
                            industry=getattr(company_info, 'industry', ''),
                            market_cap=getattr(company_info, 'market_cap', 0),
                            fundamentals={
                                'employees': getattr(company_info, 'employees', 0),
                                'country': getattr(company_info, 'country', ''),
                                'currency': getattr(company_info, 'currency', 'USD')
                            },
                            source=source_name
                        )
                        
                        logger.info(f"Successfully got company data from {source_name}")
                        return unified_data
                        
            except Exception as e:
                logger.warning(f"Failed to get company data from {source_name}: {e}")
                continue
        
        logger.error("All sources failed for company data, returning mock data")
        return self._get_mock_company_data(symbol)
    
    async def get_financial_statements(self, symbol: str, statement_type: str = 'income', period: str = 'annual') -> List[Dict[str, Any]]:
        """Get financial statements"""
        
        for source_name in [self.primary_source] + self.fallback_sources:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                if hasattr(source, 'get_financial_statements'):
                    statements = await source.get_financial_statements(symbol, statement_type, period)
                    
                    # Add source information
                    for stmt in statements:
                        stmt['source'] = source_name
                    
                    logger.info(f"Successfully got {len(statements)} statements from {source_name}")
                    return statements
                    
            except Exception as e:
                logger.warning(f"Failed to get financial statements from {source_name}: {e}")
                continue
        
        logger.error("All sources failed for financial statements, returning mock data")
        return self._get_mock_financial_statements(symbol, statement_type, period)
    
    async def get_technical_indicators(self, symbol: str, indicators: List[str]) -> List[Dict[str, Any]]:
        """Get technical indicators"""
        
        # Try Finance Toolkit first for analysis
        analysis_sources = ['finance_toolkit'] + [self.primary_source] + self.fallback_sources
        
        for source_name in analysis_sources:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                if hasattr(source, 'get_technical_indicators'):
                    indicators_data = await source.get_technical_indicators(symbol, indicators)
                    
                    # Convert to unified format
                    unified_indicators = []
                    for indicator in indicators_data:
                        unified_indicators.append({
                            'symbol': symbol,
                            'indicator_name': getattr(indicator, 'indicator_name', ''),
                            'value': getattr(indicator, 'value', 0),
                            'signal': getattr(indicator, 'signal', ''),
                            'confidence': getattr(indicator, 'confidence', 0),
                            'timestamp': getattr(indicator, 'timestamp', datetime.now()),
                            'source': source_name
                        })
                    
                    logger.info(f"Successfully got {len(unified_indicators)} indicators from {source_name}")
                    return unified_indicators
                    
            except Exception as e:
                logger.warning(f"Failed to get technical indicators from {source_name}: {e}")
                continue
        
        logger.error("All sources failed for technical indicators, returning mock data")
        return self._get_mock_technical_indicators(symbol, indicators)
    
    async def get_sec_filings(self, symbol: str, filing_type: str = None, count: int = 10) -> List[Dict[str, Any]]:
        """Get SEC filings (EDGAR only)"""
        
        edgar_source = self.sources.get('edgar')
        if not edgar_source or not edgar_source.enabled:
            logger.warning("EDGAR source not available")
            return self._get_mock_sec_filings(symbol, filing_type, count)
        
        try:
            # First get company info to get CIK
            company_info = await edgar_source.search_company_by_ticker(symbol)
            if not company_info:
                logger.warning(f"Could not find CIK for {symbol}")
                return self._get_mock_sec_filings(symbol, filing_type, count)
            
            # Get filings
            filings = await edgar_source.get_company_filings(company_info.cik, filing_type, count)
            
            # Convert to unified format
            unified_filings = []
            for filing in filings:
                unified_filings.append({
                    'symbol': symbol,
                    'company_name': filing.company_name,
                    'cik': filing.cik,
                    'filing_type': filing.filing_type,
                    'filing_date': filing.filing_date,
                    'accession_number': filing.accession_number,
                    'document_url': filing.document_url,
                    'description': filing.description,
                    'source': 'edgar'
                })
            
            logger.info(f"Successfully got {len(unified_filings)} SEC filings")
            return unified_filings
            
        except Exception as e:
            logger.error(f"Failed to get SEC filings: {e}")
        
        return self._get_mock_sec_filings(symbol, filing_type, count)
    
    async def get_financial_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive financial analysis"""
        
        analysis_sources = ['finance_toolkit', 'openbb'] + self.fallback_sources
        
        for source_name in analysis_sources:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                analysis_data = {}
                
                # Get financial ratios
                if hasattr(source, 'get_financial_ratios'):
                    ratios = await source.get_financial_ratios(symbol)
                    analysis_data['ratios'] = [
                        {
                            'name': ratio.ratio_name,
                            'value': ratio.value,
                            'category': ratio.category,
                            'description': ratio.description
                        } for ratio in ratios
                    ]
                
                # Get valuation metrics
                if hasattr(source, 'get_valuation_metrics'):
                    valuations = await source.get_valuation_metrics(symbol)
                    analysis_data['valuations'] = [
                        {
                            'metric': valuation.metric_name,
                            'value': valuation.value,
                            'method': valuation.method
                        } for valuation in valuations
                    ]
                
                # Get risk metrics
                if hasattr(source, 'get_risk_metrics'):
                    risks = await source.get_risk_metrics(symbol)
                    analysis_data['risks'] = [
                        {
                            'type': risk.risk_type,
                            'value': risk.value,
                            'interpretation': risk.interpretation
                        } for risk in risks
                    ]
                
                # Get technical signals
                if hasattr(source, 'get_technical_signals'):
                    signals = await source.get_technical_signals(symbol)
                    analysis_data['signals'] = [
                        {
                            'type': signal.signal_type,
                            'signal': signal.signal_value,
                            'confidence': signal.confidence
                        } for signal in signals
                    ]
                
                analysis_data['source'] = source_name
                analysis_data['timestamp'] = datetime.now().isoformat()
                
                logger.info(f"Successfully got financial analysis from {source_name}")
                return analysis_data
                
            except Exception as e:
                logger.warning(f"Failed to get financial analysis from {source_name}: {e}")
                continue
        
        logger.error("All sources failed for financial analysis, returning mock data")
        return self._get_mock_financial_analysis(symbol)
    
    def get_sources_status(self) -> Dict[str, Any]:
        """Get status of all data sources"""
        
        status = {
            'primary_source': self.primary_source,
            'fallback_sources': self.fallback_sources,
            'sources': {}
        }
        
        for source_name, source in self.sources.items():
            if source:
                source_status = source.get_status()
                status['sources'][source_name] = DataSourceStatus(
                    name=source_status['provider'],
                    enabled=source_status['enabled'],
                    available=source_status['enabled'],
                    features=source_status['features'],
                    cost=source_status['cost'],
                    api_key_required=source_status['api_key_required']
                )
            else:
                status['sources'][source_name] = DataSourceStatus(
                    name=source_name,
                    enabled=False,
                    available=False,
                    features=[],
                    cost='N/A',
                    api_key_required=False
                )
        
        return status
    
    # Mock data methods for fallback
    def _get_mock_quotes(self, symbols: List[str]) -> List[UnifiedMarketData]:
        """Generate mock quotes"""
        import random
        quotes = []
        
        for symbol in symbols:
            base_price = 100.0 + random.uniform(-50, 150)
            quotes.append(UnifiedMarketData(
                symbol=symbol,
                price=base_price,
                volume=random.randint(100000, 10000000),
                timestamp=datetime.now(),
                source='mock',
                additional_data={
                    'high': base_price * 1.02,
                    'low': base_price * 0.98,
                    'change': random.uniform(-5, 5),
                    'change_percent': random.uniform(-5, 5)
                }
            ))
        
        return quotes
    
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
                'source': 'mock'
            })
            
            current_date += timedelta(days=1)
        
        return data
    
    def _get_mock_company_data(self, symbol: str) -> UnifiedCompanyData:
        """Generate mock company data"""
        import random
        return UnifiedCompanyData(
            symbol=symbol,
            company_name=f"{symbol} Corporation",
            sector="Technology",
            industry="Software",
            market_cap=random.uniform(1e9, 1e12),
            fundamentals={
                'employees': random.randint(1000, 100000),
                'country': 'United States',
                'currency': 'USD'
            },
            source='mock'
        )
    
    def _get_mock_financial_statements(self, symbol: str, statement_type: str, period: str) -> List[Dict[str, Any]]:
        """Generate mock financial statements"""
        import random
        statements = []
        
        for i in range(4):
            date = datetime.now() - timedelta(days=365 * i)
            statements.append({
                'symbol': symbol,
                'statement_type': statement_type,
                'period': period,
                'date': date,
                'revenue': random.uniform(1e8, 1e11),
                'net_income': random.uniform(1e7, 1e10),
                'total_assets': random.uniform(1e9, 1e12),
                'total_liabilities': random.uniform(1e8, 1e11),
                'cash_flow': random.uniform(1e7, 1e10),
                'source': 'mock'
            })
        
        return statements
    
    def _get_mock_technical_indicators(self, symbol: str, indicators: List[str]) -> List[Dict[str, Any]]:
        """Generate mock technical indicators"""
        import random
        mock_indicators = []
        
        for indicator in indicators:
            mock_indicators.append({
                'symbol': symbol,
                'indicator_name': indicator,
                'value': random.uniform(0, 100),
                'signal': random.choice(['BUY', 'SELL', 'HOLD']),
                'confidence': random.uniform(0.6, 0.9),
                'timestamp': datetime.now(),
                'source': 'mock'
            })
        
        return mock_indicators
    
    def _get_mock_sec_filings(self, symbol: str, filing_type: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock SEC filings"""
        import random
        filings = []
        
        for i in range(min(count, 10)):
            filing_date = datetime.now() - timedelta(days=random.randint(1, 365))
            filings.append({
                'symbol': symbol,
                'company_name': f"{symbol} Corporation",
                'cik': str(random.randint(1000000000, 9999999999)),
                'filing_type': filing_type if filing_type else random.choice(['10-K', '10-Q', '8-K']),
                'filing_date': filing_date,
                'accession_number': f"0000{random.randint(1000000000, 9999999999)}-{filing_date.strftime('%Y%m%d')}-0000{i:04d}",
                'document_url': f"https://www.sec.gov/Archives/edgar/data/{random.randint(1000000000, 9999999999)}/mock-{i}.txt",
                'description': f"Mock {filing_type if filing_type else 'SEC'} filing",
                'source': 'mock'
            })
        
        return filings
    
    def _get_mock_financial_analysis(self, symbol: str) -> Dict[str, Any]:
        """Generate mock financial analysis"""
        import random
        return {
            'ratios': [
                {'name': 'Return on Equity', 'value': random.uniform(0.05, 0.25), 'category': 'Profitability', 'description': 'Measures profitability relative to shareholder equity'},
                {'name': 'Current Ratio', 'value': random.uniform(1.0, 3.0), 'category': 'Liquidity', 'description': 'Measures ability to pay short-term obligations'}
            ],
            'valuations': [
                {'metric': 'P/E Ratio', 'value': random.uniform(15, 35), 'method': 'Price to Earnings'},
                {'metric': 'P/B Ratio', 'value': random.uniform(1.0, 5.0), 'method': 'Price to Book'}
            ],
            'risks': [
                {'type': 'Beta', 'value': random.uniform(0.5, 2.0), 'interpretation': 'Moderate volatility, similar to market risk'},
                {'type': 'Volatility', 'value': random.uniform(0.1, 0.4), 'interpretation': 'Moderate volatility, normal price movements'}
            ],
            'signals': [
                {'type': 'Moving Average', 'signal': random.choice(['BUY', 'SELL', 'HOLD']), 'confidence': random.uniform(0.6, 0.9)},
                {'type': 'RSI', 'signal': random.choice(['BUY', 'SELL', 'HOLD']), 'confidence': random.uniform(0.6, 0.9)}
            ],
            'source': 'mock',
            'timestamp': datetime.now().isoformat()
        }

# Factory function
def get_free_data_sources_manager(config: Dict[str, Any] = None) -> FreeDataSourcesManager:
    """Factory function to get free data sources manager"""
    return FreeDataSourcesManager(config)
