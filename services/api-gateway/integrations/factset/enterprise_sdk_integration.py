"""
FactSet Enterprise SDK Integration for Veyra

This module provides integration with FactSet's Enterprise SDK for:
- Portfolio analytics
- Market data access
- Entity mapping
- Financial analytics
- Risk calculations
- Institutional-grade data structures
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from decimal import Decimal

from .financial_intelligence_layer import (
    FinancialEntity, MarketData, FinancialStatement, AnalyticsData,
    DataSource, get_financial_intelligence_layer
)

logger = logging.getLogger(__name__)


@dataclass
class PortfolioAnalytics:
    """Portfolio analytics data structure"""
    portfolio_id: str
    total_value: float
    total_return: float
    risk_metrics: Dict[str, float]
    attribution: Dict[str, float]
    sector_allocation: Dict[str, float]
    geographic_allocation: Dict[str, float]
    currency_exposure: Dict[str, float]
    var_metrics: Dict[str, float]
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    volatility: float
    beta: float
    alpha: float
    information_ratio: float
    tracking_error: float


@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    symbol: str
    var_1d: float
    var_5d: float
    var_30d: float
    cvar_1d: float
    cvar_5d: float
    cvar_30d: float
    beta: float
    correlation_to_market: float
    volatility: float
    max_drawdown: float
    downside_deviation: float
    upside_capture: float
    downside_capture: float


class FactSetEnterpriseSDK:
    """Main FactSet Enterprise SDK integration class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.factset_config = config.get('factset', {})
        self._init_clients()
        self.financial_intelligence = get_financial_intelligence_layer(config)
    
    def _init_clients(self):
        """Initialize FactSet SDK clients"""
        try:
            # Import FactSet Enterprise SDK
            from factset.enterprise_sdk import (
                PortfolioAnalyticsClient,
                MarketDataClient,
                EntityClient,
                AnalyticsClient,
                RiskClient,
                SignalsClient,
                FormulaClient
            )
            
            # Initialize clients with credentials
            self.portfolio_client = PortfolioAnalyticsClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.market_data_client = MarketDataClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.entity_client = EntityClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.analytics_client = AnalyticsClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.risk_client = RiskClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.signals_client = SignalsClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.formula_client = FormulaClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            logger.info("FactSet Enterprise SDK clients initialized successfully")
            
        except ImportError:
            logger.warning("FactSet Enterprise SDK not available. Using mock implementation.")
            self._init_mock_clients()
    
    def _init_mock_clients(self):
        """Initialize mock clients for development/testing"""
        self.portfolio_client = None
        self.market_data_client = None
        self.entity_client = None
        self.analytics_client = None
        self.risk_client = None
        self.signals_client = None
        self.formula_client = None
    
    async def get_portfolio_analytics(self, portfolio_id: str, 
                                   benchmark_id: Optional[str] = None) -> PortfolioAnalytics:
        """Get comprehensive portfolio analytics"""
        try:
            if self.portfolio_client:
                # Use FactSet Portfolio Analytics Engine
                response = await self.portfolio_client.get_portfolio_analytics(
                    portfolio_id=portfolio_id,
                    benchmark_id=benchmark_id,
                    include_risk_metrics=True,
                    include_attribution=True,
                    include_sector_allocation=True,
                    include_geographic_allocation=True
                )
                
                return PortfolioAnalytics(
                    portfolio_id=response.portfolio_id,
                    total_value=response.total_value,
                    total_return=response.total_return,
                    risk_metrics=response.risk_metrics,
                    attribution=response.attribution,
                    sector_allocation=response.sector_allocation,
                    geographic_allocation=response.geographic_allocation,
                    currency_exposure=response.currency_exposure,
                    var_metrics=response.var_metrics,
                    sharpe_ratio=response.sharpe_ratio,
                    sortino_ratio=response.sortino_ratio,
                    max_drawdown=response.max_drawdown,
                    volatility=response.volatility,
                    beta=response.beta,
                    alpha=response.alpha,
                    information_ratio=response.information_ratio,
                    tracking_error=response.tracking_error
                )
            else:
                # Mock implementation
                return PortfolioAnalytics(
                    portfolio_id=portfolio_id,
                    total_value=1000000.0,
                    total_return=0.15,
                    risk_metrics={'var_1d': 0.02, 'var_5d': 0.045, 'var_30d': 0.089},
                    attribution={'sector': 0.05, 'security': 0.08, 'currency': 0.02},
                    sector_allocation={'Technology': 0.35, 'Healthcare': 0.20, 'Finance': 0.15},
                    geographic_allocation={'US': 0.65, 'Europe': 0.25, 'Asia': 0.10},
                    currency_exposure={'USD': 0.70, 'EUR': 0.20, 'JPY': 0.10},
                    var_metrics={'var_1d': 0.02, 'var_5d': 0.045, 'var_30d': 0.089},
                    sharpe_ratio=1.45,
                    sortino_ratio=1.89,
                    max_drawdown=-0.12,
                    volatility=0.15,
                    beta=1.05,
                    alpha=0.03,
                    information_ratio=0.65,
                    tracking_error=0.046
                )
                
        except Exception as e:
            logger.error(f"Error getting portfolio analytics for {portfolio_id}: {e}")
            raise
    
    async def get_entity_mapping(self, symbols: List[str]) -> Dict[str, FinancialEntity]:
        """Get entity mapping for symbols using FactSet Entity API"""
        try:
            entity_mapping = {}
            
            if self.entity_client:
                # Use FactSet Entity API for batch mapping
                response = await self.entity_client.batch_get_entities(symbols)
                
                for entity_data in response.entities:
                    entity = FinancialEntity(
                        symbol=entity_data.symbol,
                        name=entity_data.name,
                        asset_type=entity_data.asset_type,
                        exchange=entity_data.exchange,
                        currency=entity_data.currency,
                        sector=entity_data.sector,
                        industry=entity_data.industry,
                        market_cap=entity_data.market_cap,
                        factset_entity_id=entity_data.entity_id,
                        additional_ids=entity_data.additional_ids
                    )
                    entity_mapping[entity.symbol] = entity
            else:
                # Mock implementation - use Financial Intelligence Layer
                for symbol in symbols:
                    entity = await self.financial_intelligence.get_entity(symbol)
                    if entity:
                        entity_mapping[symbol] = entity
            
            return entity_mapping
            
        except Exception as e:
            logger.error(f"Error getting entity mapping: {e}")
            return {}
    
    async def get_risk_metrics(self, symbols: List[str], 
                             benchmark_id: Optional[str] = None) -> Dict[str, RiskMetrics]:
        """Get risk metrics for symbols"""
        try:
            risk_metrics = {}
            
            if self.risk_client:
                # Use FactSet Risk API
                response = await self.risk_client.get_risk_metrics(
                    symbols=symbols,
                    benchmark_id=benchmark_id,
                    include_var=True,
                    include_cvar=True,
                    include_greeks=True
                )
                
                for symbol, risk_data in response.risk_metrics.items():
                    risk_metrics[symbol] = RiskMetrics(
                        symbol=symbol,
                        var_1d=risk_data.var_1d,
                        var_5d=risk_data.var_5d,
                        var_30d=risk_data.var_30d,
                        cvar_1d=risk_data.cvar_1d,
                        cvar_5d=risk_data.cvar_5d,
                        cvar_30d=risk_data.cvar_30d,
                        beta=risk_data.beta,
                        correlation_to_market=risk_data.correlation_to_market,
                        volatility=risk_data.volatility,
                        max_drawdown=risk_data.max_drawdown,
                        downside_deviation=risk_data.downside_deviation,
                        upside_capture=risk_data.upside_capture,
                        downside_capture=risk_data.downside_capture
                    )
            else:
                # Mock implementation
                for symbol in symbols:
                    risk_metrics[symbol] = RiskMetrics(
                        symbol=symbol,
                        var_1d=0.02,
                        var_5d=0.045,
                        var_30d=0.089,
                        cvar_1d=0.025,
                        cvar_5d=0.055,
                        cvar_30d=0.11,
                        beta=1.05,
                        correlation_to_market=0.75,
                        volatility=0.15,
                        max_drawdown=-0.12,
                        downside_deviation=0.09,
                        upside_capture=1.1,
                        downside_capture=0.95
                    )
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Error getting risk metrics: {e}")
            return {}
    
    async def get_trading_signals(self, symbols: List[str], 
                               signal_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Get trading signals using FactSet Signals API"""
        try:
            signals = {}
            
            if self.signals_client:
                # Use FactSet Signals API
                response = await self.signals_client.get_signals(
                    symbols=symbols,
                    signal_types=signal_types,
                    include_sentiment=True,
                    include_technical=True,
                    include_fundamental=True
                )
                
                for symbol, symbol_signals in response.signals.items():
                    signals[symbol] = [
                        {
                            'signal_type': signal.signal_type,
                            'value': signal.value,
                            'confidence': signal.confidence,
                            'timestamp': signal.timestamp,
                            'description': signal.description
                        }
                        for signal in symbol_signals
                    ]
            else:
                # Mock implementation
                for symbol in symbols:
                    signals[symbol] = [
                        {
                            'signal_type': 'momentum',
                            'value': 0.75,
                            'confidence': 0.82,
                            'timestamp': datetime.now(),
                            'description': 'Strong upward momentum detected'
                        },
                        {
                            'signal_type': 'sentiment',
                            'value': 0.65,
                            'confidence': 0.78,
                            'timestamp': datetime.now(),
                            'description': 'Positive market sentiment'
                        }
                    ]
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting trading signals: {e}")
            return {}
    
    async def execute_custom_formula(self, formula: str, symbols: List[str], 
                                  start_date: datetime, end_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Execute custom financial formulas using FactSet Formula API"""
        try:
            results = {}
            
            if self.formula_client:
                # Use FactSet Formula API
                response = await self.formula_client.execute_formula(
                    formula=formula,
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date
                )
                
                for symbol, data in response.results.items():
                    results[symbol] = [
                        {
                            'date': entry.date,
                            'value': entry.value,
                            'formula': formula
                        }
                        for entry in data
                    ]
            else:
                # Mock implementation
                for symbol in symbols:
                    results[symbol] = [
                        {
                            'date': datetime.now() - timedelta(days=i),
                            'value': 100.0 + i * 0.5,
                            'formula': formula
                        }
                        for i in range(30)
                    ]
            
            return results
            
        except Exception as e:
            logger.error(f"Error executing custom formula: {e}")
            return {}
    
    async def get_market_data_batch(self, symbols: List[str], 
                                 start_date: datetime, end_date: datetime,
                                 fields: List[str] = None) -> Dict[str, List[MarketData]]:
        """Get batch market data for multiple symbols"""
        try:
            market_data = {}
            
            if self.market_data_client:
                # Use FactSet Market Data API for batch requests
                response = await self.market_data_client.get_batch_timeseries(
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    fields=fields or ['price', 'volume', 'bid', 'ask', 'high', 'low', 'open', 'close']
                )
                
                for symbol, data in response.data.items():
                    market_data[symbol] = [
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
                        for entry in data
                    ]
            else:
                # Use Financial Intelligence Layer as fallback
                for symbol in symbols:
                    data = await self.financial_intelligence.get_market_data(
                        symbol, start_date, end_date, DataSource.FACTSET
                    )
                    if data:
                        market_data[symbol] = data
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting batch market data: {e}")
            return {}
    
    async def get_financial_statements_batch(self, symbols: List[str], 
                                          statement_types: List[str] = None) -> Dict[str, List[FinancialStatement]]:
        """Get batch financial statements"""
        try:
            statements = {}
            
            if self.analytics_client:
                # Use FactSet Analytics API for batch requests
                response = await self.analytics_client.get_batch_financial_statements(
                    symbols=symbols,
                    statement_types=statement_types or ['income', 'balance', 'cash_flow']
                )
                
                for symbol, symbol_statements in response.statements.items():
                    statements[symbol] = [
                        FinancialStatement(
                            symbol=symbol,
                            statement_type=stmt.statement_type,
                            period_type=stmt.period_type,
                            period_end=stmt.period_end,
                            data=stmt.data,
                            currency=stmt.currency,
                            source=DataSource.FACTSET
                        )
                        for stmt in symbol_statements
                    ]
            else:
                # Use Financial Intelligence Layer as fallback
                for symbol in symbols:
                    data = await self.financial_intelligence.get_financial_statements(
                        symbol, DataSource.FACTSET
                    )
                    if data:
                        statements[symbol] = data
            
            return statements
            
        except Exception as e:
            logger.error(f"Error getting batch financial statements: {e}")
            return {}


# Singleton instance
_factset_sdk = None

def get_factset_sdk(config: Dict[str, Any] = None) -> FactSetEnterpriseSDK:
    """Get or create FactSet SDK singleton"""
    global _factset_sdk
    if _factset_sdk is None:
        if config is None:
            raise ValueError("Config required for first initialization")
        _factset_sdk = FactSetEnterpriseSDK(config)
    return _factset_sdk
