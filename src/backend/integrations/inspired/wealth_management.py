"""
Wealth Management Module - Inspired by FactSet Recipes
Free open-source alternative using free data sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

from ..free.free_data_sources import get_free_data_sources_manager

logger = logging.getLogger(__name__)

@dataclass
class ClientAlert:
    client_id: str
    alert_type: str
    message: str
    severity: str
    timestamp: datetime
    action_required: bool

@dataclass
class ModelPortfolio:
    portfolio_id: str
    name: str
    description: str
    assets: List[Dict[str, Any]]
    analytics: Dict[str, Any]
    risk_metrics: Dict[str, Any]

@dataclass
class ProposalAnalytics:
    proposal_id: str
    client_id: str
    model_portfolio_id: str
    expected_return: float
    risk_metrics: Dict[str, Any]
    attribution: Dict[str, Any]

class WealthManagementModule:
    """Wealth management features inspired by FactSet recipes using free data sources"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data_manager = get_free_data_sources_manager(config.get('data_sources', {}))
        self.cache = {}
        self.cache_ttl = 600  # 10 minutes
        
        logger.info("Wealth Management Module initialized")
    
    async def get_client_signals_alerts(self, client_portfolios: List[str]) -> List[ClientAlert]:
        """
        Inspired by: "Stay on top of Salesforce Accounts with FactSet Signals"
        Generate alerts for client portfolios based on market signals
        """
        alerts = []
        
        for portfolio_id in client_portfolios:
            try:
                # Get portfolio holdings (mock for now)
                holdings = await self._get_portfolio_holdings(portfolio_id)
                
                # Get market data for holdings
                symbols = [holding['symbol'] for holding in holdings]
                market_data = await self.data_manager.get_real_time_quotes(symbols)
                
                # Generate alerts based on signals
                for holding in holdings:
                    symbol = holding['symbol']
                    current_data = next((m for m in market_data if m.symbol == symbol), None)
                    
                    if current_data:
                        # Check for significant price movements
                        if abs(current_data.additional_data.get('change_percent', 0)) > 5:
                            alerts.append(ClientAlert(
                                client_id=portfolio_id,
                                alert_type="PRICE_MOVEMENT",
                                message=f"{symbol} moved {current_data.additional_data.get('change_percent', 0):.2f}%",
                                severity="HIGH" if abs(current_data.additional_data.get('change_percent', 0)) > 10 else "MEDIUM",
                                timestamp=datetime.now(),
                                action_required=True
                            ))
                        
                        # Check for volume spikes
                        if current_data.volume > holding.get('avg_volume', 0) * 2:
                            alerts.append(ClientAlert(
                                client_id=portfolio_id,
                                alert_type="VOLUME_SPIKE",
                                message=f"Unusual volume in {symbol}: {current_data.volume:,}",
                                severity="MEDIUM",
                                timestamp=datetime.now(),
                                action_required=False
                            ))
                
            except Exception as e:
                logger.error(f"Error generating alerts for {portfolio_id}: {e}")
        
        return alerts
    
    async def create_model_portfolio_analytics(self, portfolio_config: Dict[str, Any]) -> ModelPortfolio:
        """
        Inspired by: "Model Portfolio Derived Analytics for Business Development Tools"
        Create model portfolios with comprehensive analytics
        """
        try:
            # Extract portfolio configuration
            assets = portfolio_config.get('assets', [])
            portfolio_name = portfolio_config.get('name', 'Model Portfolio')
            description = portfolio_config.get('description', '')
            
            # Get market data for all assets
            symbols = [asset['symbol'] for asset in assets]
            market_data = await self.data_manager.get_real_time_quotes(symbols)
            
            # Calculate portfolio analytics
            total_value = sum(asset.get('weight', 0) * 1000000 for asset in assets)  # Assume $1M base
            analytics = {
                'total_value': total_value,
                'expected_return': self._calculate_portfolio_return(assets, market_data),
                'dividend_yield': self._calculate_portfolio_yield(assets, market_data),
                'sector_allocation': self._calculate_sector_allocation(assets),
                'geographic_allocation': self._calculate_geographic_allocation(assets)
            }
            
            # Calculate risk metrics
            risk_metrics = await self._calculate_portfolio_risk(assets)
            
            return ModelPortfolio(
                portfolio_id=f"MP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=portfolio_name,
                description=description,
                assets=assets,
                analytics=analytics,
                risk_metrics=risk_metrics
            )
            
        except Exception as e:
            logger.error(f"Error creating model portfolio analytics: {e}")
            raise
    
    async def generate_proposal_analytics(self, model_portfolio: ModelPortfolio, client_profile: Dict[str, Any]) -> ProposalAnalytics:
        """
        Inspired by: "Model Portfolio Derived Analytics for Business Development Tools"
        Generate comprehensive analytics for client proposals
        """
        try:
            # Calculate expected return based on model and client profile
            expected_return = self._adjust_return_for_client(model_portfolio.analytics['expected_return'], client_profile)
            
            # Calculate risk metrics for client
            risk_metrics = await self._calculate_client_risk_metrics(model_portfolio, client_profile)
            
            # Generate attribution analysis
            attribution = await self._generate_attribution_analysis(model_portfolio, client_profile)
            
            return ProposalAnalytics(
                proposal_id=f"PROP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                client_id=client_profile.get('client_id', ''),
                model_portfolio_id=model_portfolio.portfolio_id,
                expected_return=expected_return,
                risk_metrics=risk_metrics,
                attribution=attribution
            )
            
        except Exception as e:
            logger.error(f"Error generating proposal analytics: {e}")
            raise
    
    async def get_performance_data_for_digital_portal(self, portfolio_id: str) -> Dict[str, Any]:
        """
        Inspired by: "Consistent, High Quality Performance Data for Digital Portals"
        Generate performance data for digital portals
        """
        try:
            # Get portfolio holdings
            holdings = await self._get_portfolio_holdings(portfolio_id)
            symbols = [holding['symbol'] for holding in holdings]
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            performance_data = {
                'portfolio_id': portfolio_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'holdings_performance': [],
                'portfolio_metrics': {},
                'benchmark_comparison': {}
            }
            
            # Calculate performance for each holding
            for holding in holdings:
                symbol = holding['symbol']
                historical_data = await self.data_manager.get_historical_data(symbol, start_date, end_date)
                
                if historical_data:
                    initial_price = historical_data[0]['close']
                    final_price = historical_data[-1]['close']
                    total_return = (final_price - initial_price) / initial_price
                    
                    performance_data['holdings_performance'].append({
                        'symbol': symbol,
                        'weight': holding.get('weight', 0),
                        'initial_price': initial_price,
                        'final_price': final_price,
                        'total_return': total_return,
                        'contribution': total_return * holding.get('weight', 0)
                    })
            
            # Calculate portfolio metrics
            performance_data['portfolio_metrics'] = self._calculate_portfolio_performance_metrics(
                performance_data['holdings_performance']
            )
            
            # Benchmark comparison (using S&P 500 as benchmark)
            benchmark_data = await self.data_manager.get_historical_data('SPY', start_date, end_date)
            if benchmark_data:
                benchmark_return = (benchmark_data[-1]['close'] - benchmark_data[0]['close']) / benchmark_data[0]['close']
                performance_data['benchmark_comparison'] = {
                    'benchmark_return': benchmark_return,
                    'portfolio_return': performance_data['portfolio_metrics']['total_return'],
                    'alpha': performance_data['portfolio_metrics']['total_return'] - benchmark_return
                }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error generating performance data for {portfolio_id}: {e}")
            raise
    
    async def create_synchronized_performance_metrics(self, portfolio_ids: List[str]) -> Dict[str, Any]:
        """
        Inspired by: "Synchronized Performance Metrics and Flexible Reporting"
        Generate synchronized performance metrics across multiple portfolios
        """
        try:
            synchronized_data = {
                'generated_at': datetime.now().isoformat(),
                'portfolios': {},
                'aggregate_metrics': {},
                'attribution_analysis': {}
            }
            
            all_holdings = []
            portfolio_weights = {}
            
            # Get data for all portfolios
            for portfolio_id in portfolio_ids:
                portfolio_data = await self.get_performance_data_for_digital_portal(portfolio_id)
                synchronized_data['portfolios'][portfolio_id] = portfolio_data
                
                # Collect holdings for aggregate analysis
                for holding_perf in portfolio_data['holdings_performance']:
                    all_holdings.append({
                        'symbol': holding_perf['symbol'],
                        'weight': holding_perf['weight'],
                        'return': holding_perf['total_return'],
                        'portfolio_id': portfolio_id
                    })
                
                portfolio_weights[portfolio_id] = portfolio_data.get('portfolio_metrics', {}).get('total_value', 0)
            
            # Calculate aggregate metrics
            synchronized_data['aggregate_metrics'] = self._calculate_aggregate_metrics(all_holdings, portfolio_weights)
            
            # Generate attribution analysis
            synchronized_data['attribution_analysis'] = self._generate_cross_portfolio_attribution(all_holdings)
            
            return synchronized_data
            
        except Exception as e:
            logger.error(f"Error creating synchronized performance metrics: {e}")
            raise
    
    async def get_advisor_dashboard_data(self, advisor_id: str) -> Dict[str, Any]:
        """
        Inspired by: "One Convenient Dashboard to Maximize Advisor Efficiency"
        Create comprehensive advisor dashboard
        """
        try:
            dashboard_data = {
                'advisor_id': advisor_id,
                'generated_at': datetime.now().isoformat(),
                'client_summary': {},
                'portfolio_overview': {},
                'market_alerts': [],
                'performance_summary': {},
                'action_items': []
            }
            
            # Get advisor's clients (mock data)
            client_portfolios = await self._get_advisor_clients(advisor_id)
            
            # Generate client summary
            dashboard_data['client_summary'] = {
                'total_clients': len(client_portfolios),
                'total_aum': sum(portfolio.get('aum', 0) for portfolio in client_portfolios),
                'active_portfolios': len([p for p in client_portfolios if p.get('status') == 'active']),
                'new_clients_this_month': len([p for p in client_portfolios if self._is_new_client(p)])
            }
            
            # Generate portfolio overview
            portfolio_ids = [p['id'] for p in client_portfolios]
            synchronized_data = await self.create_synchronized_performance_metrics(portfolio_ids)
            dashboard_data['portfolio_overview'] = synchronized_data['aggregate_metrics']
            
            # Get market alerts
            dashboard_data['market_alerts'] = await self.get_client_signals_alerts(portfolio_ids)
            
            # Generate performance summary
            dashboard_data['performance_summary'] = {
                'best_performing_client': self._get_best_performing_client(synchronized_data),
                'worst_performing_client': self._get_worst_performing_client(synchronized_data),
                'average_return': synchronized_data['aggregate_metrics'].get('total_return', 0),
                'total_alpha': synchronized_data['aggregate_metrics'].get('alpha', 0)
            }
            
            # Generate action items
            dashboard_data['action_items'] = self._generate_advisor_action_items(
                dashboard_data['market_alerts'],
                dashboard_data['performance_summary']
            )
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating advisor dashboard for {advisor_id}: {e}")
            raise
    
    # Helper methods
    async def _get_portfolio_holdings(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """Get portfolio holdings (mock implementation)"""
        # This would typically connect to a database
        return [
            {'symbol': 'AAPL', 'weight': 0.25, 'avg_volume': 50000000},
            {'symbol': 'MSFT', 'weight': 0.20, 'avg_volume': 30000000},
            {'symbol': 'GOOGL', 'weight': 0.15, 'avg_volume': 25000000},
            {'symbol': 'AMZN', 'weight': 0.10, 'avg_volume': 40000000},
            {'symbol': 'TSLA', 'weight': 0.10, 'avg_volume': 100000000}
        ]
    
    def _calculate_portfolio_return(self, assets: List[Dict[str, Any]], market_data: List) -> float:
        """Calculate expected portfolio return"""
        total_return = 0
        for asset in assets:
            symbol = asset['symbol']
            weight = asset.get('weight', 0)
            
            # Get historical return (mock calculation)
            market_item = next((m for m in market_data if m.symbol == symbol), None)
            if market_item:
                # Mock expected return based on current metrics
                expected_return = 0.08  # 8% average return
                total_return += weight * expected_return
        
        return total_return
    
    def _calculate_portfolio_yield(self, assets: List[Dict[str, Any]], market_data: List) -> float:
        """Calculate portfolio dividend yield"""
        total_yield = 0
        for asset in assets:
            symbol = asset['symbol']
            weight = asset.get('weight', 0)
            
            # Mock dividend yield
            dividend_yield = 0.02  # 2% average dividend yield
            total_yield += weight * dividend_yield
        
        return total_yield
    
    def _calculate_sector_allocation(self, assets: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sector allocation"""
        # Mock sector allocation
        return {
            'Technology': 0.60,
            'Healthcare': 0.15,
            'Financial': 0.10,
            'Consumer': 0.10,
            'Other': 0.05
        }
    
    def _calculate_geographic_allocation(self, assets: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate geographic allocation"""
        # Mock geographic allocation
        return {
            'United States': 0.75,
            'Europe': 0.15,
            'Asia': 0.08,
            'Other': 0.02
        }
    
    async def _calculate_portfolio_risk(self, assets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        # Mock risk calculation
        return {
            'volatility': 0.15,  # 15% annual volatility
            'beta': 1.1,
            'var_95': 0.05,  # 5% Value at Risk
            'sharpe_ratio': 0.8,
            'max_drawdown': 0.12
        }
    
    def _adjust_return_for_client(self, base_return: float, client_profile: Dict[str, Any]) -> float:
        """Adjust expected return based on client profile"""
        risk_tolerance = client_profile.get('risk_tolerance', 'moderate')
        
        if risk_tolerance == 'conservative':
            return base_return * 0.7
        elif risk_tolerance == 'aggressive':
            return base_return * 1.3
        else:
            return base_return
    
    async def _calculate_client_risk_metrics(self, model_portfolio: ModelPortfolio, client_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk metrics for client"""
        base_risk = model_portfolio.risk_metrics
        risk_adjustment = client_profile.get('risk_tolerance', 'moderate')
        
        adjustment_factor = {
            'conservative': 0.7,
            'moderate': 1.0,
            'aggressive': 1.3
        }.get(risk_adjustment, 1.0)
        
        return {
            key: value * adjustment_factor for key, value in base_risk.items()
        }
    
    async def _generate_attribution_analysis(self, model_portfolio: ModelPortfolio, client_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate attribution analysis"""
        return {
            'sector_attribution': {
                'Technology': 0.045,
                'Healthcare': 0.015,
                'Financial': 0.010,
                'Consumer': 0.008,
                'Other': 0.002
            },
            'security_selection': 0.020,
            'asset_allocation': 0.060,
            'interaction_effect': 0.005
        }
    
    def _calculate_portfolio_performance_metrics(self, holdings_performance: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        total_return = sum(hp['contribution'] for hp in holdings_performance)
        
        # Calculate other metrics
        returns = [hp['total_return'] for hp in holdings_performance]
        weights = [hp['weight'] for hp in holdings_performance]
        
        # Weighted average return
        weighted_return = sum(r * w for r, w in zip(returns, weights))
        
        return {
            'total_return': total_return,
            'weighted_return': weighted_return,
            'best_performing': max(holdings_performance, key=lambda x: x['total_return']),
            'worst_performing': min(holdings_performance, key=lambda x: x['total_return']),
            'volatility': 0.15  # Mock calculation
        }
    
    def _calculate_aggregate_metrics(self, all_holdings: List[Dict[str, Any]], portfolio_weights: Dict[str, float]) -> Dict[str, Any]:
        """Calculate aggregate metrics across portfolios"""
        total_weight = sum(portfolio_weights.values())
        
        # Weighted average return
        weighted_returns = []
        for holding in all_holdings:
            portfolio_weight = portfolio_weights.get(holding['portfolio_id'], 0) / total_weight
            weighted_return = holding['return'] * holding['weight'] * portfolio_weight
            weighted_returns.append(weighted_return)
        
        return {
            'total_return': sum(weighted_returns),
            'total_aum': sum(portfolio_weights.values()),
            'number_of_holdings': len(set(h['symbol'] for h in all_holdings)),
            'alpha': 0.025  # Mock alpha
        }
    
    def _generate_cross_portfolio_attribution(self, all_holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cross-portfolio attribution analysis"""
        symbol_returns = {}
        for holding in all_holdings:
            symbol = holding['symbol']
            if symbol not in symbol_returns:
                symbol_returns[symbol] = []
            symbol_returns[symbol].append(holding['return'])
        
        # Calculate attribution by symbol
        attribution = {}
        for symbol, returns in symbol_returns.items():
            avg_return = sum(returns) / len(returns)
            attribution[symbol] = avg_return
        
        return attribution
    
    async def _get_advisor_clients(self, advisor_id: str) -> List[Dict[str, Any]]:
        """Get advisor's clients (mock implementation)"""
        return [
            {'id': 'client_1', 'name': 'John Doe', 'aum': 1000000, 'status': 'active', 'created_date': '2023-01-15'},
            {'id': 'client_2', 'name': 'Jane Smith', 'aum': 2500000, 'status': 'active', 'created_date': '2023-03-20'},
            {'id': 'client_3', 'name': 'Bob Johnson', 'aum': 500000, 'status': 'active', 'created_date': '2023-06-10'}
        ]
    
    def _is_new_client(self, client: Dict[str, Any]) -> bool:
        """Check if client is new (joined in last 30 days)"""
        created_date = datetime.fromisoformat(client['created_date'])
        return (datetime.now() - created_date).days <= 30
    
    def _get_best_performing_client(self, synchronized_data: Dict[str, Any]) -> str:
        """Get best performing client"""
        # Mock implementation
        return 'client_2'
    
    def _get_worst_performing_client(self, synchronized_data: Dict[str, Any]) -> str:
        """Get worst performing client"""
        # Mock implementation
        return 'client_3'
    
    def _generate_advisor_action_items(self, alerts: List[ClientAlert], performance_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate action items for advisor"""
        action_items = []
        
        # High priority alerts
        high_priority_alerts = [a for a in alerts if a.severity == 'HIGH' and a.action_required]
        for alert in high_priority_alerts[:5]:  # Limit to top 5
            action_items.append({
                'type': 'ALERT',
                'priority': 'HIGH',
                'description': alert.message,
                'client_id': alert.client_id,
                'due_date': (datetime.now() + timedelta(days=1)).isoformat()
            })
        
        # Performance review items
        if performance_summary.get('average_return', 0) < 0:
            action_items.append({
                'type': 'PERFORMANCE_REVIEW',
                'priority': 'MEDIUM',
                'description': 'Review underperforming portfolios',
                'due_date': (datetime.now() + timedelta(days=7)).isoformat()
            })
        
        return action_items

# Factory function
def get_wealth_management_module(config: Dict[str, Any] = None) -> WealthManagementModule:
    """Factory function to get wealth management module"""
    return WealthManagementModule(config)
