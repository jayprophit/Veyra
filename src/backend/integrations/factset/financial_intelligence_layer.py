"""
Financial Intelligence Layer - Unified Abstraction for Financial Data Providers

This layer provides a unified interface for integrating multiple financial data providers
including FactSet, Polygon, CoinGecko, Binance, FRED, SEC, and DeFi APIs.

Architecture:
- Provider-agnostic interface
- Normalized data schemas
- AI-agent friendly API
- Unified financial ontology
- Scalable plugin system
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Supported financial data sources"""
    FACTSET = "factset"
    POLYGON = "polygon"
    COINGECKO = "coingecko"
    BINANCE = "binance"
    FRED = "fred"
    SEC = "sec"
    DEFIPULSE = "defipulse"
    COINBASE = "coinbase"
    YAHOO = "yahoo"


@dataclass
class FinancialEntity:
    """Unified financial entity representation"""
    symbol: str
    name: str
    asset_type: str  # stock, etf, crypto, bond, commodity
    exchange: str
    currency: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    factset_entity_id: Optional[str] = None
    additional_ids: Dict[str, str] = None  # Other provider IDs


@dataclass
class MarketData:
    """Unified market data structure"""
    symbol: str
    timestamp: datetime
    price: float
    volume: Optional[int] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    close: Optional[float] = None
    source: DataSource = DataSource.FACTSET


@dataclass
class FinancialStatement:
    """Unified financial statement structure"""
    symbol: str
    statement_type: str  # income, balance, cash_flow
    period_type: str  # quarterly, annual
    period_end: datetime
    data: Dict[str, float]
    currency: str
    source: DataSource = DataSource.FACTSET


@dataclass
class AnalyticsData:
    """Unified analytics data structure"""
    symbol: str
    metric_type: str  # valuation, risk, momentum, etc.
    value: float
    timestamp: datetime
    confidence: Optional[float] = None
    source: DataSource = DataSource.FACTSET


class DataProvider(ABC):
    """Abstract base class for financial data providers"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}
        self.rate_limiter = None
        
    @abstractmethod
    async def get_entity(self, symbol: str) -> Optional[FinancialEntity]:
        """Get entity information for a symbol"""
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[MarketData]:
        """Get historical market data"""
        pass
    
    @abstractmethod
    async def get_real_time_data(self, symbols: List[str]) -> List[MarketData]:
        """Get real-time market data"""
        pass
    
    @abstractmethod
    async def get_financial_statements(self, symbol: str) -> List[FinancialStatement]:
        """Get financial statements"""
        pass
    
    @abstractmethod
    async def get_analytics(self, symbol: str, metrics: List[str]) -> List[AnalyticsData]:
        """Get analytics data"""
        pass


class FactSetProvider(DataProvider):
    """FactSet data provider implementation"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.base_url = "https://api.factset.com"
        self._init_clients()
    
    def _init_clients(self):
        """Initialize FactSet SDK clients"""
        try:
            # Import FactSet SDK components
            from factset.enterprise_sdk import (
                PortfolioAnalyticsClient,
                MarketDataClient,
                EntityClient,
                AnalyticsClient
            )
            
            self.portfolio_client = PortfolioAnalyticsClient(
                username=self.config.get('username'),
                password=self.config.get('password')
            )
            self.market_data_client = MarketDataClient(
                username=self.config.get('username'),
                password=self.config.get('password')
            )
            self.entity_client = EntityClient(
                username=self.config.get('username'),
                password=self.config.get('password')
            )
            self.analytics_client = AnalyticsClient(
                username=self.config.get('username'),
                password=self.config.get('password')
            )
            
            logger.info("FactSet SDK clients initialized successfully")
            
        except ImportError:
            logger.warning("FactSet SDK not available. Using mock implementation.")
            self._init_mock_clients()
    
    def _init_mock_clients(self):
        """Initialize mock clients for development"""
        self.portfolio_client = None
        self.market_data_client = None
        self.entity_client = None
        self.analytics_client = None
    
    async def get_entity(self, symbol: str) -> Optional[FinancialEntity]:
        """Get entity information using FactSet Entity API"""
        try:
            if self.entity_client:
                # Use FactSet Entity API
                response = await self.entity_client.get_entity(symbol)
                return FinancialEntity(
                    symbol=response.symbol,
                    name=response.name,
                    asset_type=response.asset_type,
                    exchange=response.exchange,
                    currency=response.currency,
                    sector=response.sector,
                    industry=response.industry,
                    factset_entity_id=response.entity_id
                )
            else:
                # Mock implementation
                return FinancialEntity(
                    symbol=symbol,
                    name=f"Mock {symbol} Company",
                    asset_type="stock",
                    exchange="NYSE",
                    currency="USD",
                    sector="Technology",
                    factset_entity_id=f"FS-{symbol}"
                )
        except Exception as e:
            logger.error(f"Error getting entity for {symbol}: {e}")
            return None
    
    async def get_market_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[MarketData]:
        """Get market data using FactSet Market Data API"""
        try:
            if self.market_data_client:
                # Use FactSet Market Data API
                response = await self.market_data_client.get_timeseries(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    fields=['price', 'volume', 'bid', 'ask', 'high', 'low', 'open', 'close']
                )
                
                return [
                    MarketData(
                        symbol=symbol,
                        timestamp=entry.timestamp,
                        price=entry.price,
                        volume=entry.volume,
                        bid=entry.bid,
                        ask=entry.ask,
                        high=entry.high,
                        low=entry.low,
                        open=entry.open,
                        close=entry.close,
                        source=DataSource.FACTSET
                    )
                    for entry in response.data
                ]
            else:
                # Mock implementation
                return []
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return []
    
    async def get_real_time_data(self, symbols: List[str]) -> List[MarketData]:
        """Get real-time market data"""
        try:
            if self.market_data_client:
                # Use FactSet real-time API
                response = await self.market_data_client.get_real_time(symbols)
                
                return [
                    MarketData(
                        symbol=item.symbol,
                        timestamp=datetime.now(),
                        price=item.price,
                        volume=item.volume,
                        bid=item.bid,
                        ask=item.ask,
                        source=DataSource.FACTSET
                    )
                    for item in response.data
                ]
            else:
                # Mock implementation
                return []
        except Exception as e:
            logger.error(f"Error getting real-time data: {e}")
            return []
    
    async def get_financial_statements(self, symbol: str) -> List[FinancialStatement]:
        """Get financial statements using FactSet Fundamentals API"""
        try:
            if self.analytics_client:
                # Use FactSet Fundamentals API
                response = await self.analytics_client.get_financial_statements(symbol)
                
                return [
                    FinancialStatement(
                        symbol=symbol,
                        statement_type=stmt.statement_type,
                        period_type=stmt.period_type,
                        period_end=stmt.period_end,
                        data=stmt.data,
                        currency=stmt.currency,
                        source=DataSource.FACTSET
                    )
                    for stmt in response.statements
                ]
            else:
                # Mock implementation
                return []
        except Exception as e:
            logger.error(f"Error getting financial statements for {symbol}: {e}")
            return []
    
    async def get_analytics(self, symbol: str, metrics: List[str]) -> List[AnalyticsData]:
        """Get analytics data using FactSet Analytics API"""
        try:
            if self.analytics_client:
                # Use FactSet Analytics API
                response = await self.analytics_client.get_analytics(symbol, metrics)
                
                return [
                    AnalyticsData(
                        symbol=symbol,
                        metric_type=metric.metric_type,
                        value=metric.value,
                        timestamp=metric.timestamp,
                        confidence=metric.confidence,
                        source=DataSource.FACTSET
                    )
                    for metric in response.metrics
                ]
            else:
                # Mock implementation
                return []
        except Exception as e:
            logger.error(f"Error getting analytics for {symbol}: {e}")
            return []


class FinancialIntelligenceLayer:
    """Main Financial Intelligence Layer - Unified interface for all financial data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[DataSource, DataProvider] = {}
        self.entity_cache: Dict[str, FinancialEntity] = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize all configured data providers"""
        # Initialize FactSet if configured
        if 'factset' in self.config:
            factset_config = self.config['factset']
            self.providers[DataSource.FACTSET] = FactSetProvider(
                api_key=factset_config.get('api_key'),
                config=factset_config
            )
        
        # Initialize other providers as needed
        # Polygon, CoinGecko, Binance, etc.
        
        logger.info(f"Initialized {len(self.providers)} data providers")
    
    async def get_entity(self, symbol: str, preferred_source: DataSource = DataSource.FACTSET) -> Optional[FinancialEntity]:
        """Get entity information with fallback to other providers"""
        # Check cache first
        if symbol in self.entity_cache:
            return self.entity_cache[symbol]
        
        # Try preferred source first
        if preferred_source in self.providers:
            entity = await self.providers[preferred_source].get_entity(symbol)
            if entity:
                self.entity_cache[symbol] = entity
                return entity
        
        # Try other providers
        for source, provider in self.providers.items():
            if source != preferred_source:
                entity = await provider.get_entity(symbol)
                if entity:
                    self.entity_cache[symbol] = entity
                    return entity
        
        return None
    
    async def get_market_data(self, symbol: str, start_date: datetime, end_date: datetime, 
                           source: DataSource = DataSource.FACTSET) -> List[MarketData]:
        """Get market data from specified source"""
        if source in self.providers:
            return await self.providers[source].get_market_data(symbol, start_date, end_date)
        return []
    
    async def get_real_time_data(self, symbols: List[str], 
                              source: DataSource = DataSource.FACTSET) -> List[MarketData]:
        """Get real-time market data"""
        if source in self.providers:
            return await self.providers[source].get_real_time_data(symbols)
        return []
    
    async def get_financial_statements(self, symbol: str, 
                                   source: DataSource = DataSource.FACTSET) -> List[FinancialStatement]:
        """Get financial statements"""
        if source in self.providers:
            return await self.providers[source].get_financial_statements(symbol)
        return []
    
    async def get_analytics(self, symbol: str, metrics: List[str], 
                          source: DataSource = DataSource.FACTSET) -> List[AnalyticsData]:
        """Get analytics data"""
        if source in self.providers:
            return await self.providers[source].get_analytics(symbol, metrics)
        return []
    
    async def get_portfolio_analytics(self, symbols: List[str], 
                                 analytics_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get portfolio analytics using FactSet PA Engine"""
        if DataSource.FACTSET in self.providers:
            provider = self.providers[DataSource.FACTSET]
            if hasattr(provider, 'portfolio_client') and provider.portfolio_client:
                try:
                    # Use FactSet Portfolio Analytics Engine
                    response = await provider.portfolio_client.get_portfolio_analytics(
                        symbols=symbols,
                        **analytics_config
                    )
                    return response.analytics
                except Exception as e:
                    logger.error(f"Error getting portfolio analytics: {e}")
        
        return {}
    
    async def get_signals(self, symbols: List[str], signal_types: List[str]) -> List[Dict[str, Any]]:
        """Get trading signals using FactSet Signals API"""
        if DataSource.FACTSET in self.providers:
            provider = self.providers[DataSource.FACTSET]
            if hasattr(provider, 'analytics_client') and provider.analytics_client:
                try:
                    # Use FactSet Signals API
                    response = await provider.analytics_client.get_signals(
                        symbols=symbols,
                        signal_types=signal_types
                    )
                    return response.signals
                except Exception as e:
                    logger.error(f"Error getting signals: {e}")
        
        return []
    
    def get_supported_sources(self) -> List[DataSource]:
        """Get list of supported data sources"""
        return list(self.providers.keys())


# Singleton instance for global access
_financial_intelligence_layer = None

def get_financial_intelligence_layer(config: Dict[str, Any] = None) -> FinancialIntelligenceLayer:
    """Get or create the Financial Intelligence Layer singleton"""
    global _financial_intelligence_layer
    if _financial_intelligence_layer is None:
        if config is None:
            raise ValueError("Config required for first initialization")
        _financial_intelligence_layer = FinancialIntelligenceLayer(config)
    return _financial_intelligence_layer
