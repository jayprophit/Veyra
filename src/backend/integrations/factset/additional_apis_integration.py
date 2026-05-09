"""
Additional FactSet APIs Integration for Financial Master

This module provides integration with high-value FactSet APIs:
- Real-Time Quotes API
- FactSet Fundamentals API  
- Signals API
- Open:Risk API
- FactSet Estimates API
- Optimization Engine API
- Natural Language Processing API
- FactSet Entity API
- FactSet Mergers and Acquisitions API
- Security Intelligence API
- FactSet Quant Factor Library API
- Conversational API (Mercury)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import pandas as pd
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class RealTimeQuote:
    """Real-time quote data structure"""
    symbol: str
    last_price: float
    bid_price: float
    ask_price: float
    volume: int
    high_price: float
    low_price: float
    open_price: float
    close_price: float
    timestamp: datetime
    exchange: str
    currency: str


@dataclass
class FundamentalData:
    """Fundamental data structure"""
    symbol: str
    period_end: datetime
    fiscal_year: int
    fiscal_quarter: Optional[int]
    revenue: float
    net_income: float
    gross_profit: float
    operating_income: float
    ebitda: float
    total_assets: float
    total_liabilities: float
    shareholders_equity: float
    currency: str


@dataclass
class SignalEvent:
    """Signal event data structure"""
    symbol: str
    signal_type: str
    confidence: float
    timestamp: datetime
    description: str
    impact_score: float
    source: str


@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    symbol: str
    factor_exposures: Dict[str, float]
    factor_returns: Dict[str, float]
    var_1d: float
    var_5d: float
    var_30d: float
    cvar_1d: float
    beta: float
    volatility: float
    tracking_error: float


@dataclass
class EstimateData:
    """Estimate data structure"""
    symbol: str
    metric_name: str
    fiscal_period: str
    consensus_value: float
    high_estimate: float
    low_estimate: float
    number_of_analysts: int
    last_updated: datetime
    currency: str


@dataclass
class OptimizationResult:
    """Portfolio optimization result"""
    portfolio_id: str
    optimal_weights: Dict[str, float]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    constraints: Dict[str, Any]
    optimization_date: datetime


class AdditionalFactSetAPIs:
    """Additional FactSet APIs integration class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.factset_config = config.get('factset', {})
        self._init_clients()
    
    def _init_clients(self):
        """Initialize additional FactSet API clients"""
        try:
            # Import FactSet API clients
            from factset.realtime_quotes import RealTimeQuotesClient
            from factset.fundamentals import FundamentalsClient
            from factset.signals import SignalsClient
            from factset.open_risk import OpenRiskClient
            from factset.estimates import EstimatesClient
            from factset.optimization import OptimizationClient
            from factset.nlp import NaturalLanguageProcessingClient
            from factset.entity import EntityClient
            from factset.mergers_acquisitions import MergersAcquisitionsClient
            from factset.security_intelligence import SecurityIntelligenceClient
            from factset.quant_factors import QuantFactorLibraryClient
            from factset.conversational import ConversationalClient
            
            # Initialize clients
            self.realtime_quotes_client = RealTimeQuotesClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.fundamentals_client = FundamentalsClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.signals_client = SignalsClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.open_risk_client = OpenRiskClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.estimates_client = EstimatesClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.optimization_client = OptimizationClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.nlp_client = NaturalLanguageProcessingClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.entity_client = EntityClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.ma_client = MergersAcquisitionsClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.security_intelligence_client = SecurityIntelligenceClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.quant_factors_client = QuantFactorLibraryClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            self.conversational_client = ConversationalClient(
                username=self.factset_config.get('username'),
                password=self.factset_config.get('password'),
                api_key=self.factset_config.get('api_key')
            )
            
            logger.info("Additional FactSet API clients initialized successfully")
            
        except ImportError:
            logger.warning("Additional FactSet APIs not available. Using mock implementation.")
            self._init_mock_clients()
    
    def _init_mock_clients(self):
        """Initialize mock clients for development"""
        self.realtime_quotes_client = None
        self.fundamentals_client = None
        self.signals_client = None
        self.open_risk_client = None
        self.estimates_client = None
        self.optimization_client = None
        self.nlp_client = None
        self.entity_client = None
        self.ma_client = None
        self.security_intelligence_client = None
        self.quant_factors_client = None
        self.conversational_client = None
    
    async def get_real_time_quotes(self, symbols: List[str]) -> List[RealTimeQuote]:
        """Get real-time quotes for symbols"""
        try:
            if self.realtime_quotes_client:
                # Use FactSet Real-Time Quotes API
                response = await self.realtime_quotes_client.get_quotes(symbols)
                
                return [
                    RealTimeQuote(
                        symbol=quote.symbol,
                        last_price=quote.last_price,
                        bid_price=quote.bid_price,
                        ask_price=quote.ask_price,
                        volume=quote.volume,
                        high_price=quote.high_price,
                        low_price=quote.low_price,
                        open_price=quote.open_price,
                        close_price=quote.close_price,
                        timestamp=quote.timestamp,
                        exchange=quote.exchange,
                        currency=quote.currency
                    )
                    for quote in response.quotes
                ]
            else:
                # Mock implementation
                return [
                    RealTimeQuote(
                        symbol=symbol,
                        last_price=100.0 + hash(symbol) % 50,
                        bid_price=99.5 + hash(symbol) % 50,
                        ask_price=100.5 + hash(symbol) % 50,
                        volume=1000000,
                        high_price=102.0 + hash(symbol) % 50,
                        low_price=98.0 + hash(symbol) % 50,
                        open_price=99.0 + hash(symbol) % 50,
                        close_price=99.0 + hash(symbol) % 50,
                        timestamp=datetime.now(),
                        exchange="NYSE",
                        currency="USD"
                    )
                    for symbol in symbols
                ]
                
        except Exception as e:
            logger.error(f"Error getting real-time quotes: {e}")
            return []
    
    async def get_fundamentals(self, symbols: List[str], 
                               periods: int = 4) -> Dict[str, List[FundamentalData]]:
        """Get fundamental data for symbols"""
        try:
            fundamentals_data = {}
            
            if self.fundamentals_client:
                # Use FactSet Fundamentals API
                response = await self.fundamentals_client.get_fundamentals(
                    symbols=symbols,
                    periods=periods,
                    statement_types=['income', 'balance', 'cash_flow']
                )
                
                for symbol, data in response.fundamentals.items():
                    fundamentals_data[symbol] = [
                        FundamentalData(
                            symbol=symbol,
                            period_end=stmt.period_end,
                            fiscal_year=stmt.fiscal_year,
                            fiscal_quarter=stmt.fiscal_quarter,
                            revenue=stmt.revenue,
                            net_income=stmt.net_income,
                            gross_profit=stmt.gross_profit,
                            operating_income=stmt.operating_income,
                            ebitda=stmt.ebitda,
                            total_assets=stmt.total_assets,
                            total_liabilities=stmt.total_liabilities,
                            shareholders_equity=stmt.shareholders_equity,
                            currency=stmt.currency
                        )
                        for stmt in data
                    ]
            else:
                # Mock implementation
                for symbol in symbols:
                    fundamentals_data[symbol] = [
                        FundamentalData(
                            symbol=symbol,
                            period_end=datetime.now() - timedelta(days=90*i),
                            fiscal_year=2024,
                            fiscal_quarter=4-i,
                            revenue=1000000000 + hash(symbol) * 100000,
                            net_income=100000000 + hash(symbol) * 10000,
                            gross_profit=300000000 + hash(symbol) * 30000,
                            operating_income=150000000 + hash(symbol) * 15000,
                            ebitda=200000000 + hash(symbol) * 20000,
                            total_assets=5000000000 + hash(symbol) * 500000,
                            total_liabilities=2000000000 + hash(symbol) * 200000,
                            shareholders_equity=3000000000 + hash(symbol) * 300000,
                            currency="USD"
                        )
                        for i in range(min(periods, 4))
                    ]
            
            return fundamentals_data
            
        except Exception as e:
            logger.error(f"Error getting fundamentals: {e}")
            return {}
    
    async def get_signals(self, symbols: List[str], 
                         signal_types: List[str] = None) -> Dict[str, List[SignalEvent]]:
        """Get AI-driven signals for symbols"""
        try:
            signals_data = {}
            
            if self.signals_client:
                # Use FactSet Signals API
                response = await self.signals_client.get_signals(
                    symbols=symbols,
                    signal_types=signal_types or ['earnings', 'merger', 'analyst_upgrade']
                )
                
                for symbol, signals in response.signals.items():
                    signals_data[symbol] = [
                        SignalEvent(
                            symbol=symbol,
                            signal_type=signal.signal_type,
                            confidence=signal.confidence,
                            timestamp=signal.timestamp,
                            description=signal.description,
                            impact_score=signal.impact_score,
                            source=signal.source
                        )
                        for signal in signals
                    ]
            else:
                # Mock implementation
                for symbol in symbols:
                    signals_data[symbol] = [
                        SignalEvent(
                            symbol=symbol,
                            signal_type="earnings_surprise",
                            confidence=0.85,
                            timestamp=datetime.now(),
                            description="Positive earnings surprise detected",
                            impact_score=0.75,
                            source="FactSet Signals"
                        ),
                        SignalEvent(
                            symbol=symbol,
                            signal_type="analyst_upgrade",
                            confidence=0.72,
                            timestamp=datetime.now() - timedelta(hours=2),
                            description="Analyst upgrade from Hold to Buy",
                            impact_score=0.60,
                            source="FactSet Signals"
                        )
                    ]
            
            return signals_data
            
        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return {}
    
    async def get_risk_metrics(self, symbols: List[str], 
                               factor_model: str = "fama_french_3_factor") -> Dict[str, RiskMetrics]:
        """Get advanced risk metrics using Open:Risk API"""
        try:
            risk_data = {}
            
            if self.open_risk_client:
                # Use FactSet Open:Risk API
                response = await self.open_risk_client.calculate_risk_metrics(
                    symbols=symbols,
                    factor_model=factor_model,
                    time_horizons=[1, 5, 30]  # days
                )
                
                for symbol, metrics in response.risk_metrics.items():
                    risk_data[symbol] = RiskMetrics(
                        symbol=symbol,
                        factor_exposures=metrics.factor_exposures,
                        factor_returns=metrics.factor_returns,
                        var_1d=metrics.var_1d,
                        var_5d=metrics.var_5d,
                        var_30d=metrics.var_30d,
                        cvar_1d=metrics.cvar_1d,
                        beta=metrics.beta,
                        volatility=metrics.volatility,
                        tracking_error=metrics.tracking_error
                    )
            else:
                # Mock implementation
                for symbol in symbols:
                    risk_data[symbol] = RiskMetrics(
                        symbol=symbol,
                        factor_exposures={
                            'market': 1.0 + hash(symbol) % 100 / 100,
                            'size': -0.2 + hash(symbol) % 50 / 100,
                            'value': 0.3 + hash(symbol) % 60 / 100,
                            'momentum': 0.1 + hash(symbol) % 40 / 100
                        },
                        factor_returns={
                            'market': 0.0008,
                            'size': 0.0002,
                            'value': 0.0001,
                            'momentum': 0.0003
                        },
                        var_1d=0.02 + hash(symbol) % 30 / 1000,
                        var_5d=0.045 + hash(symbol) % 50 / 1000,
                        var_30d=0.089 + hash(symbol) % 80 / 1000,
                        cvar_1d=0.025 + hash(symbol) % 40 / 1000,
                        beta=1.05 + hash(symbol) % 50 / 100,
                        volatility=0.15 + hash(symbol) % 30 / 100,
                        tracking_error=0.04 + hash(symbol) % 20 / 100
                    )
            
            return risk_data
            
        except Exception as e:
            logger.error(f"Error getting risk metrics: {e}")
            return {}
    
    async def get_estimates(self, symbols: List[str], 
                          metrics: List[str] = None) -> Dict[str, List[EstimateData]]:
        """Get consensus estimates for symbols"""
        try:
            estimates_data = {}
            
            if self.estimates_client:
                # Use FactSet Estimates API
                response = await self.estimates_client.get_estimates(
                    symbols=symbols,
                    metrics=metrics or ['eps', 'revenue', 'ebitda'],
                    fiscal_years=[2024, 2025]
                )
                
                for symbol, estimates in response.estimates.items():
                    estimates_data[symbol] = [
                        EstimateData(
                            symbol=symbol,
                            metric_name=estimate.metric_name,
                            fiscal_period=estimate.fiscal_period,
                            consensus_value=estimate.consensus_value,
                            high_estimate=estimate.high_estimate,
                            low_estimate=estimate.low_estimate,
                            number_of_analysts=estimate.number_of_analysts,
                            last_updated=estimate.last_updated,
                            currency=estimate.currency
                        )
                        for estimate in estimates
                    ]
            else:
                # Mock implementation
                for symbol in symbols:
                    estimates_data[symbol] = [
                        EstimateData(
                            symbol=symbol,
                            metric_name="EPS",
                            fiscal_period="2024Q4",
                            consensus_value=5.25 + hash(symbol) % 100 / 100,
                            high_estimate=5.50 + hash(symbol) % 100 / 100,
                            low_estimate=5.00 + hash(symbol) % 100 / 100,
                            number_of_analysts=25,
                            last_updated=datetime.now() - timedelta(days=1),
                            currency="USD"
                        ),
                        EstimateData(
                            symbol=symbol,
                            metric_name="Revenue",
                            fiscal_period="2024",
                            consensus_value=50000000000 + hash(symbol) * 1000000,
                            high_estimate=52000000000 + hash(symbol) * 1000000,
                            low_estimate=48000000000 + hash(symbol) * 1000000,
                            number_of_analysts=30,
                            last_updated=datetime.now() - timedelta(days=2),
                            currency="USD"
                        )
                    ]
            
            return estimates_data
            
        except Exception as e:
            logger.error(f"Error getting estimates: {e}")
            return {}
    
    async def optimize_portfolio(self, symbols: List[str], 
                              constraints: Dict[str, Any] = None) -> OptimizationResult:
        """Optimize portfolio using Optimization Engine API"""
        try:
            if self.optimization_client:
                # Use FactSet Optimization Engine API
                response = await self.optimization_client.optimize_portfolio(
                    symbols=symbols,
                    constraints=constraints or {},
                    objective='max_sharpe_ratio',
                    time_horizon=252  # trading days
                )
                
                return OptimizationResult(
                    portfolio_id=response.portfolio_id,
                    optimal_weights=response.optimal_weights,
                    expected_return=response.expected_return,
                    expected_risk=response.expected_risk,
                    sharpe_ratio=response.sharpe_ratio,
                    constraints=response.constraints,
                    optimization_date=datetime.now()
                )
            else:
                # Mock implementation
                total_weight = 0.0
                optimal_weights = {}
                
                for i, symbol in enumerate(symbols):
                    weight = (1.0 / len(symbols)) + (hash(symbol) % 100 - 50) / 1000
                    optimal_weights[symbol] = max(0.0, weight)
                    total_weight += optimal_weights[symbol]
                
                # Normalize weights
                if total_weight > 0:
                    for symbol in optimal_weights:
                        optimal_weights[symbol] /= total_weight
                
                return OptimizationResult(
                    portfolio_id=f"optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    optimal_weights=optimal_weights,
                    expected_return=0.12,
                    expected_risk=0.15,
                    sharpe_ratio=0.80,
                    constraints=constraints or {},
                    optimization_date=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            raise
    
    async def analyze_text(self, text: str, 
                         analysis_types: List[str] = None) -> Dict[str, Any]:
        """Analyze text using Natural Language Processing API"""
        try:
            if self.nlp_client:
                # Use FactSet NLP API
                response = await self.nlp_client.analyze_text(
                    text=text,
                    analysis_types=analysis_types or ['sentiment', 'entities', 'topics']
                )
                
                return {
                    'sentiment': response.sentiment,
                    'entities': response.entities,
                    'topics': response.topics,
                    'confidence': response.confidence,
                    'processed_text': response.processed_text
                }
            else:
                # Mock implementation
                return {
                    'sentiment': {
                        'score': 0.65,
                        'label': 'positive',
                        'confidence': 0.82
                    },
                    'entities': [
                        {'text': 'Apple', 'type': 'ORGANIZATION', 'confidence': 0.95},
                        {'text': 'Tim Cook', 'type': 'PERSON', 'confidence': 0.88}
                    ],
                    'topics': [
                        {'topic': 'earnings', 'confidence': 0.75},
                        {'topic': 'product_launch', 'confidence': 0.60}
                    ],
                    'confidence': 0.78,
                    'processed_text': text
                }
                
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {}
    
    async def get_entity_data(self, identifiers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive entity data using Entity API"""
        try:
            entity_data = {}
            
            if self.entity_client:
                # Use FactSet Entity API
                response = await self.entity_client.get_entities(identifiers)
                
                for identifier, entity in response.entities.items():
                    entity_data[identifier] = {
                        'factset_id': entity.factset_id,
                        'name': entity.name,
                        'security_type': entity.security_type,
                        'exchange': entity.exchange,
                        'currency': entity.currency,
                        'sector': entity.sector,
                        'industry': entity.industry,
                        'country': entity.country,
                        'descriptions': entity.descriptions,
                        'identifiers': entity.identifiers
                    }
            else:
                # Mock implementation
                for identifier in identifiers:
                    entity_data[identifier] = {
                        'factset_id': f'FS-{identifier}',
                        'name': f'{identifier} Corporation',
                        'security_type': 'Common Stock',
                        'exchange': 'NYSE',
                        'currency': 'USD',
                        'sector': 'Technology',
                        'industry': 'Software',
                        'country': 'United States',
                        'descriptions': ['Leading technology company'],
                        'identifiers': {
                            'ticker': identifier,
                            'cusip': f'{identifier[:9]}',
                            'isin': f'US{identifier[:9]}1234'
                        }
                    }
            
            return entity_data
            
        except Exception as e:
            logger.error(f"Error getting entity data: {e}")
            return {}
    
    async def get_merger_data(self, symbols: List[str] = None, 
                               date_range: Dict[str, datetime] = None) -> List[Dict[str, Any]]:
        """Get M&A data using Mergers and Acquisitions API"""
        try:
            if self.ma_client:
                # Use FactSet M&A API
                response = await self.ma_client.get_deals(
                    symbols=symbols,
                    start_date=date_range.get('start') if date_range else datetime.now() - timedelta(days=365),
                    end_date=date_range.get('end') if date_range else datetime.now(),
                    deal_types=['merger', 'acquisition']
                )
                
                return [
                    {
                        'deal_id': deal.deal_id,
                        'target': deal.target,
                        'acquirer': deal.acquirer,
                        'deal_type': deal.deal_type,
                        'status': deal.status,
                        'announcement_date': deal.announcement_date,
                        'value': deal.value,
                        'currency': deal.currency,
                        'premium': deal.premium
                    }
                    for deal in response.deals
                ]
            else:
                # Mock implementation
                return [
                    {
                        'deal_id': 'DEAL_001',
                        'target': 'Target Corp',
                        'acquirer': 'Acquirer Inc',
                        'deal_type': 'acquisition',
                        'status': 'announced',
                        'announcement_date': datetime.now() - timedelta(days=30),
                        'value': 5000000000,
                        'currency': 'USD',
                        'premium': 0.25
                    }
                ]
                
        except Exception as e:
            logger.error(f"Error getting M&A data: {e}")
            return []
    
    async def get_security_intelligence(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get security intelligence using Security Intelligence API"""
        try:
            intelligence_data = {}
            
            if self.security_intelligence_client:
                # Use FactSet Security Intelligence API
                response = await self.security_intelligence_client.get_intelligence(symbols)
                
                for symbol, intelligence in response.intelligence.items():
                    intelligence_data[symbol] = {
                        'financial_standing': intelligence.financial_standing,
                        'stock_movements': intelligence.stock_movements,
                        'key_events': intelligence.key_events,
                        'risk_factors': intelligence.risk_factors,
                        'recommendations': intelligence.recommendations,
                        'confidence': intelligence.confidence
                    }
            else:
                # Mock implementation
                for symbol in symbols:
                    intelligence_data[symbol] = {
                        'financial_standing': {
                            'score': 0.75,
                            'rating': 'A-',
                            'outlook': 'Stable'
                        },
                        'stock_movements': {
                            'trend': 'bullish',
                            'momentum': 'strong',
                            'volatility': 'moderate'
                        },
                        'key_events': [
                            {'type': 'earnings', 'date': datetime.now() - timedelta(days=10)},
                            {'type': 'analyst_meeting', 'date': datetime.now() + timedelta(days=5)}
                        ],
                        'risk_factors': {
                            'market_risk': 0.3,
                            'operational_risk': 0.2,
                            'financial_risk': 0.1
                        },
                        'recommendations': [
                            {'action': 'BUY', 'confidence': 0.82},
                            {'action': 'HOLD', 'confidence': 0.15}
                        ],
                        'confidence': 0.78
                    }
            
            return intelligence_data
            
        except Exception as e:
            logger.error(f"Error getting security intelligence: {e}")
            return {}
    
    async def get_quant_factors(self, factor_universe: str = 'global_equity') -> Dict[str, Any]:
        """Get quantitative factors using Quant Factor Library API"""
        try:
            if self.quant_factors_client:
                # Use FactSet Quant Factor Library API
                response = await self.quant_factors_client.get_factors(
                    universe=factor_universe,
                    factor_categories=['value', 'momentum', 'quality', 'low_volatility', 'size']
                )
                
                return {
                    'factor_definitions': response.factor_definitions,
                    'factor_returns': response.factor_returns,
                    'factor_correlations': response.factor_correlations,
                    'universe': response.universe,
                    'last_updated': response.last_updated
                }
            else:
                # Mock implementation
                return {
                    'factor_definitions': [
                        {'name': 'book_to_market', 'description': 'Book value to market ratio'},
                        {'name': 'price_momentum_12m', 'description': '12-month price momentum'},
                        {'name': 'roe', 'description': 'Return on equity'},
                        {'name': 'volatility_12m', 'description': '12-month historical volatility'}
                    ],
                    'factor_returns': {
                        '2024-01': {'value': 0.02, 'momentum': 0.03, 'quality': 0.01},
                        '2024-02': {'value': 0.01, 'momentum': 0.02, 'quality': 0.02}
                    },
                    'factor_correlations': {
                        'value_momentum': 0.15,
                        'value_quality': 0.35,
                        'momentum_quality': -0.10
                    },
                    'universe': factor_universe,
                    'last_updated': datetime.now()
                }
                
        except Exception as e:
            logger.error(f"Error getting quant factors: {e}")
            return {}
    
    async def conversational_query(self, query: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process conversational query using Mercury API"""
        try:
            if self.conversational_client:
                # Use FactSet Conversational API
                response = await self.conversational_client.process_query(
                    query=query,
                    context=context or {}
                )
                
                return {
                    'answer': response.answer,
                    'confidence': response.confidence,
                    'sources': response.sources,
                    'follow_up_questions': response.follow_up_questions,
                    'query_type': response.query_type
                }
            else:
                # Mock implementation
                return {
                    'answer': f"Based on the available data, here's information about your query: {query}",
                    'confidence': 0.85,
                    'sources': ['FactSet Database', 'Market Data'],
                    'follow_up_questions': [
                        'Would you like more detailed analysis?',
                        'Do you need information about specific time periods?'
                    ],
                    'query_type': 'information_request'
                }
                
        except Exception as e:
            logger.error(f"Error processing conversational query: {e}")
            return {}


# Singleton instance
_additional_apis = None

def get_additional_factset_apis(config: Dict[str, Any] = None) -> AdditionalFactSetAPIs:
    """Get or create Additional FactSet APIs singleton"""
    global _additional_apis
    if _additional_apis is None:
        if config is None:
            raise ValueError("Config required for first initialization")
        _additional_apis = AdditionalFactSetAPIs(config)
    return _additional_apis
