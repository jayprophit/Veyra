"""
Quart-OpenAPI Integration for Veyra

This module provides integration with Quart-OpenAPI for:
- Modern async API infrastructure
- OpenAPI specification generation
- Automatic API documentation
- Request validation
- Response serialization
- Financial API best practices
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Type
from dataclasses import dataclass, asdict
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

try:
    from quart import Quart, request, jsonify, Response
    from quart_openapi import OpenAPI, openapi, validate
    from pydantic import BaseModel, Field, validator
    from quart_cors import cors
    QUART_AVAILABLE = True
except ImportError:
    QUART_AVAILABLE = False
    logging.warning("Quart-OpenAPI not available. Using mock implementation.")

logger = logging.getLogger(__name__)


class APIVersion(Enum):
    """API version enumeration"""
    V1 = "v1"
    V2 = "v2"


class HTTPStatus(Enum):
    """HTTP status codes"""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    responses: Dict[int, Dict[str, Any]]
    auth_required: bool = False
    rate_limit: Optional[int] = None


@dataclass
class APISchema:
    """API schema definition"""
    name: str
    model: Type[BaseModel]
    description: str
    example: Optional[Dict[str, Any]] = None


class QuartOpenAPIIntegration:
    """Main Quart-OpenAPI integration class for Veyra"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quart_config = config.get('quart_openapi', {})
        self.app = None
        self.openapi = None
        self.endpoints = {}
        self.schemas = {}
        self._init_app()
        self._setup_middleware()
        self._register_financial_endpoints()
    
    def _init_app(self):
        """Initialize Quart app with OpenAPI"""
        if QUART_AVAILABLE:
            self.app = Quart(__name__)
            
            # Configure OpenAPI
            self.openapi = OpenAPI(
                title="Veyra API",
                version="2.0.0",
                description="Institutional-grade financial data and analytics API",
                contact={
                    "name": "Veyra Team",
                    "email": "api@veyra.com"
                },
                license={
                    "name": "MIT License",
                    "url": "https://opensource.org/licenses/MIT"
                }
            )
            
            # Initialize OpenAPI with app
            self.openapi.init_app(self.app)
            
            logger.info("Quart-OpenAPI app initialized successfully")
        else:
            logger.warning("Quart-OpenAPI not available. Using mock implementation.")
            self._init_mock_app()
    
    def _init_mock_app(self):
        """Initialize mock app for development"""
        self.app = None
        self.openapi = None
    
    def _setup_middleware(self):
        """Setup middleware for security, CORS, rate limiting"""
        if QUART_AVAILABLE and self.app:
            # CORS setup
            cors_config = self.quart_config.get('cors', {})
            cors(self.app, **cors_config)
            
            # Request logging middleware
            @self.app.before_request
            async def log_request():
                logger.info(f"API Request: {request.method} {request.path}")
            
            # Error handling middleware
            @self.app.errorhandler(Exception)
            async def handle_error(error):
                logger.error(f"API Error: {str(error)}")
                return jsonify({
                    "error": str(error),
                    "status": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    "timestamp": datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
    
    def _register_financial_endpoints(self):
        """Register financial API endpoints"""
        if not QUART_AVAILABLE:
            return
        
        # Market data endpoints
        self._register_market_data_endpoints()
        
        # Portfolio analytics endpoints
        self._register_portfolio_analytics_endpoints()
        
        # Risk management endpoints
        self._register_risk_management_endpoints()
        
        # Entity mapping endpoints
        self._register_entity_mapping_endpoints()
        
        # Analytics engines endpoints
        self._register_analytics_engines_endpoints()
        
        logger.info("Financial API endpoints registered successfully")
    
    def _register_market_data_endpoints(self):
        """Register market data API endpoints"""
        
        @self.app.route('/api/v1/market/data/<symbol>', methods=['GET'])
        @openapi.summary("Get market data for symbol")
        @openapi.description("Retrieve market data including price, volume, bid/ask")
        @openapi.parameter('symbol', str, location='path', required=True, description='Trading symbol')
        @openapi.parameter('start_date', str, location='query', description='Start date (YYYY-MM-DD)')
        @openapi.parameter('end_date', str, location='query', description='End date (YYYY-MM-DD)')
        @openapi.parameter('fields', str, location='query', description='Comma-separated fields')
        @validate
        async def get_market_data(symbol: str):
            """Get market data for a symbol"""
            try:
                # Integration with Financial Intelligence Layer
                from .financial_intelligence_layer import get_financial_intelligence_layer
                
                financial_intelligence = get_financial_intelligence_layer(self.config)
                
                # Parse query parameters
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                fields = request.args.get('fields', 'price,volume,bid,ask').split(',')
                
                # Convert dates
                if start_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                if end_date:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    end_date = datetime.now()
                
                # Get market data
                market_data = await financial_intelligence.get_market_data(
                    symbol, start_date, end_date
                )
                
                # Format response
                response_data = {
                    'symbol': symbol,
                    'data': [
                        {
                            'timestamp': data.timestamp.isoformat(),
                            'price': float(data.price),
                            'volume': data.volume,
                            'bid': float(data.bid) if data.bid else None,
                            'ask': float(data.ask) if data.ask else None,
                            'source': data.source.value
                        }
                        for data in market_data
                    ],
                    'metadata': {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat(),
                        'fields': fields,
                        'count': len(market_data)
                    }
                }
                
                return jsonify(response_data), HTTPStatus.OK.value
                
            except Exception as e:
                logger.error(f"Error getting market data for {symbol}: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
        
        @self.app.route('/api/v1/market/realtime', methods=['POST'])
        @openapi.summary("Get real-time market data")
        @openapi.description("Retrieve real-time market data for multiple symbols")
        @openapi.parameter('symbols', list, location='json', required=True, description='List of symbols')
        @validate
        async def get_real_time_market_data():
            """Get real-time market data for multiple symbols"""
            try:
                data = await request.get_json()
                symbols = data.get('symbols', [])
                
                if not symbols:
                    return jsonify({
                        'error': 'Symbols list is required',
                        'status': HTTPStatus.BAD_REQUEST.value,
                        'timestamp': datetime.now().isoformat()
                    }), HTTPStatus.BAD_REQUEST.value
                
                # Get real-time data
                financial_intelligence = get_financial_intelligence_layer(self.config)
                
                real_time_data = await financial_intelligence.get_real_time_data(symbols)
                
                response_data = {
                    'symbols': symbols,
                    'data': [
                        {
                            'symbol': data.symbol,
                            'timestamp': data.timestamp.isoformat(),
                            'price': float(data.price),
                            'volume': data.volume,
                            'bid': float(data.bid) if data.bid else None,
                            'ask': float(data.ask) if data.ask else None,
                            'source': data.source.value
                        }
                        for data in real_time_data
                    ],
                    'metadata': {
                        'count': len(real_time_data),
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                return jsonify(response_data), HTTPStatus.OK.value
                
            except Exception as e:
                logger.error(f"Error getting real-time market data: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
    
    def _register_portfolio_analytics_endpoints(self):
        """Register portfolio analytics API endpoints"""
        
        @self.app.route('/api/v1/portfolio/<portfolio_id>/analytics', methods=['GET'])
        @openapi.summary("Get portfolio analytics")
        @openapi.description("Retrieve comprehensive portfolio analytics and metrics")
        @openapi.parameter('portfolio_id', str, location='path', required=True, description='Portfolio ID')
        @openapi.parameter('benchmark', str, location='query', description='Benchmark symbol')
        @openapi.parameter('period', str, location='query', description='Analysis period')
        @validate
        async def get_portfolio_analytics(portfolio_id: str):
            """Get portfolio analytics"""
            try:
                benchmark = request.args.get('benchmark')
                period = request.args.get('period', '1Y')
                
                # Get portfolio analytics
                from .enterprise_sdk_integration import get_factset_sdk
                factset_sdk = get_factset_sdk(self.config)
                
                analytics = await factset_sdk.get_portfolio_analytics(
                    portfolio_id, benchmark
                )
                
                response_data = {
                    'portfolio_id': portfolio_id,
                    'analytics': {
                        'total_value': analytics.total_value,
                        'total_return': analytics.total_return,
                        'risk_metrics': analytics.risk_metrics,
                        'attribution': analytics.attribution,
                        'sector_allocation': analytics.sector_allocation,
                        'geographic_allocation': analytics.geographic_allocation,
                        'currency_exposure': analytics.currency_exposure,
                        'performance_metrics': {
                            'sharpe_ratio': analytics.sharpe_ratio,
                            'sortino_ratio': analytics.sortino_ratio,
                            'max_drawdown': analytics.max_drawdown,
                            'volatility': analytics.volatility,
                            'beta': analytics.beta,
                            'alpha': analytics.alpha,
                            'information_ratio': analytics.information_ratio,
                            'tracking_error': analytics.tracking_error
                        }
                    },
                    'metadata': {
                        'benchmark': benchmark,
                        'period': period,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                return jsonify(response_data), HTTPStatus.OK.value
                
            except Exception as e:
                logger.error(f"Error getting portfolio analytics for {portfolio_id}: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
        
        @self.app.route('/api/v1/portfolio/<portfolio_id>/risk', methods=['GET'])
        @openapi.summary("Get portfolio risk metrics")
        @openapi.description("Retrieve portfolio risk metrics and VaR calculations")
        @openapi.parameter('portfolio_id', str, location='path', required=True, description='Portfolio ID')
        @openapi.parameter('confidence_levels', str, location='query', description='Confidence levels (e.g., 0.95,0.99)')
        @validate
        async def get_portfolio_risk(portfolio_id: str):
            """Get portfolio risk metrics"""
            try:
                confidence_levels_str = request.args.get('confidence_levels', '0.95,0.99')
                confidence_levels = [float(x) for x in confidence_levels_str.split(',')]
                
                # Get risk metrics
                factset_sdk = get_factset_sdk(self.config)
                
                # Get portfolio holdings first
                # This would typically come from portfolio service
                symbols = ['AAPL', 'MSFT', 'GOOGL']  # Mock symbols
                
                risk_metrics = await factset_sdk.get_risk_metrics(symbols)
                
                response_data = {
                    'portfolio_id': portfolio_id,
                    'risk_metrics': {
                        symbol: {
                            'var_1d': metrics.var_1d,
                            'var_5d': metrics.var_5d,
                            'var_30d': metrics.var_30d,
                            'cvar_1d': metrics.cvar_1d,
                            'cvar_5d': metrics.cvar_5d,
                            'cvar_30d': metrics.cvar_30d,
                            'beta': metrics.beta,
                            'correlation_to_market': metrics.correlation_to_market,
                            'volatility': metrics.volatility,
                            'max_drawdown': metrics.max_drawdown,
                            'downside_deviation': metrics.downside_deviation,
                            'upside_capture': metrics.upside_capture,
                            'downside_capture': metrics.downside_capture
                        }
                        for symbol, metrics in risk_metrics.items()
                    },
                    'metadata': {
                        'confidence_levels': confidence_levels,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                return jsonify(response_data), HTTPStatus.OK.value
                
            except Exception as e:
                logger.error(f"Error getting portfolio risk for {portfolio_id}: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
    
    def _register_risk_management_endpoints(self):
        """Register risk management API endpoints"""
        
        @self.app.route('/api/v1/risk/var', methods=['POST'])
        @openapi.summary("Calculate Value at Risk")
        @openapi.description("Calculate VaR for portfolio or individual symbols")
        @openapi.parameter('request', dict, location='json', required=True, description='VaR calculation request')
        @validate
        async def calculate_var():
            """Calculate Value at Risk"""
            try:
                data = await request.get_json()
                symbols = data.get('symbols', [])
                confidence_levels = data.get('confidence_levels', [0.95, 0.99])
                time_horizons = data.get('time_horizons', [1, 5, 30])
                
                # Calculate VaR using analytics engines
                from .analytics_engines_integration import get_analytics_engines
                from .financial_intelligence_layer import AnalyticsRequest
                
                analytics_engines = get_analytics_engines(self.config)
                
                var_request = AnalyticsRequest(
                    engine_name='var_calculation',
                    parameters={
                        'confidence_levels': confidence_levels,
                        'methods': ['historical', 'parametric', 'monte_carlo']
                    },
                    symbols=symbols,
                    start_date=datetime.now() - timedelta(days=504),
                    end_date=datetime.now()
                )
                
                var_result = await analytics_engines.run_analytics(var_request)
                
                if var_result.success:
                    response_data = {
                        'symbols': symbols,
                        'var_results': var_result.data.get('var_results', {}).to_dict('records'),
                        'var_backtesting': var_result.data.get('var_backtesting', {}).to_dict('records'),
                        'metadata': {
                            'confidence_levels': confidence_levels,
                            'time_horizons': time_horizons,
                            'execution_time': var_result.execution_time,
                            'timestamp': datetime.now().isoformat()
                        }
                    }
                    
                    return jsonify(response_data), HTTPStatus.OK.value
                else:
                    return jsonify({
                        'error': var_result.error,
                        'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                        'timestamp': datetime.now().isoformat()
                    }), HTTPStatus.INTERNAL_SERVER_ERROR.value
                    
            except Exception as e:
                logger.error(f"Error calculating VaR: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
    
    def _register_entity_mapping_endpoints(self):
        """Register entity mapping API endpoints"""
        
        @self.app.route('/api/v1/entities/mapping', methods=['POST'])
        @openapi.summary("Get entity mapping")
        @openapi.description("Map symbols to FactSet entities and get metadata")
        @openapi.parameter('request', dict, location='json', required=True, description='Entity mapping request')
        @validate
        async def get_entity_mapping():
            """Get entity mapping for symbols"""
            try:
                data = await request.get_json()
                symbols = data.get('symbols', [])
                
                if not symbols:
                    return jsonify({
                        'error': 'Symbols list is required',
                        'status': HTTPStatus.BAD_REQUEST.value,
                        'timestamp': datetime.now().isoformat()
                    }), HTTPStatus.BAD_REQUEST.value
                
                # Get entity mapping
                factset_sdk = get_factset_sdk(self.config)
                
                entity_mapping = await factset_sdk.get_entity_mapping(symbols)
                
                response_data = {
                    'symbols': symbols,
                    'entities': {
                        symbol: {
                            'symbol': entity.symbol,
                            'name': entity.name,
                            'asset_type': entity.asset_type,
                            'exchange': entity.exchange,
                            'currency': entity.currency,
                            'sector': entity.sector,
                            'industry': entity.industry,
                            'market_cap': entity.market_cap,
                            'factset_entity_id': entity.factset_entity_id,
                            'additional_ids': entity.additional_ids
                        }
                        for symbol, entity in entity_mapping.items()
                    },
                    'metadata': {
                        'count': len(entity_mapping),
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                return jsonify(response_data), HTTPStatus.OK.value
                
            except Exception as e:
                logger.error(f"Error getting entity mapping: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
    
    def _register_analytics_engines_endpoints(self):
        """Register analytics engines API endpoints"""
        
        @self.app.route('/api/v1/analytics/engines', methods=['GET'])
        @openapi.summary("Get available analytics engines")
        @openapi.description("List all available analytics engines with metadata")
        async def get_analytics_engines():
            """Get available analytics engines"""
            try:
                analytics_engines = get_analytics_engines(self.config)
                
                engines = await analytics_engines.get_available_engines()
                
                response_data = {
                    'engines': engines,
                    'metadata': {
                        'count': len(engines),
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                return jsonify(response_data), HTTPStatus.OK.value
                
            except Exception as e:
                logger.error(f"Error getting analytics engines: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
        
        @self.app.route('/api/v1/analytics/run', methods=['POST'])
        @openapi.summary("Run analytics engine")
        @openapi.description("Execute analytics engine with specified parameters")
        @openapi.parameter('request', dict, location='json', required=True, description='Analytics request')
        @validate
        async def run_analytics_engine():
            """Run analytics engine"""
            try:
                data = await request.get_json()
                
                from .analytics_engines_integration import get_analytics_engines, AnalyticsRequest
                
                analytics_request = AnalyticsRequest(
                    engine_name=data.get('engine_name'),
                    parameters=data.get('parameters', {}),
                    symbols=data.get('symbols', []),
                    start_date=datetime.fromisoformat(data.get('start_date')),
                    end_date=datetime.fromisoformat(data.get('end_date')),
                    frequency=data.get('frequency', 'daily'),
                    benchmark=data.get('benchmark')
                )
                
                analytics_engines = get_analytics_engines(self.config)
                result = await analytics_engines.run_analytics(analytics_request)
                
                if result.success:
                    response_data = {
                        'engine_name': result.engine_name,
                        'symbols': result.symbols,
                        'data': {
                            key: df.to_dict('records') if hasattr(df, 'to_dict') else df
                            for key, df in result.data.items()
                        },
                        'metadata': result.metadata,
                        'execution_time': result.execution_time,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    return jsonify(response_data), HTTPStatus.OK.value
                else:
                    return jsonify({
                        'error': result.error,
                        'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                        'timestamp': datetime.now().isoformat()
                    }), HTTPStatus.INTERNAL_SERVER_ERROR.value
                    
            except Exception as e:
                logger.error(f"Error running analytics engine: {e}")
                return jsonify({
                    'error': str(e),
                    'status': HTTPStatus.INTERNAL_SERVER_ERROR.value,
                    'timestamp': datetime.now().isoformat()
                }), HTTPStatus.INTERNAL_SERVER_ERROR.value
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI specification"""
        if self.openapi:
            return self.openapi.spec
        return {}
    
    def run_app(self, host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
        """Run the Quart application"""
        if self.app:
            logger.info(f"Starting Veyra API on {host}:{port}")
            return self.app.run(host=host, port=port, debug=debug)
        else:
            logger.error("Quart app not initialized")
            return None


# Singleton instance
_quart_openapi_integration = None

def get_quart_openapi_integration(config: Dict[str, Any] = None) -> QuartOpenAPIIntegration:
    """Get or create Quart-OpenAPI integration singleton"""
    global _quart_openapi_integration
    if _quart_openapi_integration is None:
        if config is None:
            raise ValueError("Config required for first initialization")
        _quart_openapi_integration = QuartOpenAPIIntegration(config)
    return _quart_openapi_integration
