"""
Portfolio Analytics Widgets - Inspired by FactSet Portfolio Analytics Showcase
Free open-source alternative using free data sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import numpy as np

from .widget_framework import BaseWidget, WidgetConfig, WidgetData, WidgetType
from ..integrations.inspired.portfolio_analytics import get_portfolio_analytics_module

logger = logging.getLogger(__name__)

class PortfolioPerformanceWidget(BaseWidget):
    """Portfolio performance widget showing returns, metrics, and charts"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            portfolio_id = self.config.data_config.get('portfolio_id', 'default_portfolio')
            benchmark = self.config.data_config.get('benchmark', 'SPY')
            
            # Get portfolio analytics module
            analytics = get_portfolio_analytics_module()
            
            # Get performance metrics
            performance_metrics = await analytics.calculate_performance_metrics(portfolio_id, benchmark)
            
            # Get attribution data
            attribution = await analytics.calculate_brinson_attribution(portfolio_id, benchmark)
            
            # Get performance over time
            performance_over_time = await analytics.calculate_attribution_over_time(portfolio_id, benchmark)
            
            performance_data = {
                'portfolio_id': portfolio_id,
                'benchmark': benchmark,
                'metrics': {
                    'total_return': performance_metrics.period_return,
                    'annualized_return': performance_metrics.annualized_return,
                    'volatility': performance_metrics.volatility,
                    'sharpe_ratio': performance_metrics.sharpe_ratio,
                    'max_drawdown': performance_metrics.max_drawdown,
                    'calmar_ratio': performance_metrics.calmar_ratio,
                    'beta': performance_metrics.beta,
                    'tracking_error': performance_metrics.tracking_error,
                    'information_ratio': performance_metrics.information_ratio
                },
                'attribution': {
                    'total_return': attribution.total_return,
                    'benchmark_return': attribution.benchmark_return,
                    'alpha': attribution.alpha,
                    'sector_attribution': attribution.sector_attribution,
                    'security_selection': attribution.security_selection,
                    'asset_allocation': attribution.asset_allocation,
                    'interaction_effect': attribution.interaction_effect
                },
                'performance_over_time': performance_over_time,
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=performance_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching portfolio performance data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="portfolio-performance-widget" id="{self.config.widget_id}">
            <h3>Portfolio Performance</h3>
            <div class="performance-summary">
                <div class="metrics-grid">
                    <!-- Performance metrics will be rendered here -->
                </div>
            </div>
            <div class="performance-chart">
                <!-- Performance chart will be rendered here -->
            </div>
            <div class="attribution-breakdown">
                <!-- Attribution breakdown will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'portfolio_performance',
            'config': self.config.__dict__,
            'template': self.render_html()
        }

class HoldingsBreakdownWidget(BaseWidget):
    """Holdings breakdown widget showing portfolio composition"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            portfolio_id = self.config.data_config.get('portfolio_id', 'default_portfolio')
            
            # Get portfolio holdings (mock implementation)
            holdings = await self._get_portfolio_holdings(portfolio_id)
            
            # Calculate breakdown metrics
            holdings_data = {
                'portfolio_id': portfolio_id,
                'holdings': holdings,
                'breakdown': self._calculate_holdings_breakdown(holdings),
                'sector_allocation': self._calculate_sector_allocation(holdings),
                'geographic_allocation': self._calculate_geographic_allocation(holdings),
                'top_holdings': holdings[:10],  # Top 10 holdings
                'total_value': sum(holding.get('market_value', 0) for holding in holdings),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=holdings_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching holdings breakdown data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="holdings-breakdown-widget" id="{self.config.widget_id}">
            <h3>Holdings Breakdown</h3>
            <div class="holdings-summary">
                <!-- Holdings summary will be rendered here -->
            </div>
            <div class="sector-allocation-chart">
                <!-- Sector allocation chart will be rendered here -->
            </div>
            <div class="holdings-table">
                <!-- Holdings table will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'holdings_breakdown',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _get_portfolio_holdings(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """Get portfolio holdings (mock implementation)"""
        # Mock holdings data
        holdings = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'shares': 100, 'price': 150.25, 'weight': 0.15, 'sector': 'Technology'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'shares': 50, 'price': 280.50, 'weight': 0.12, 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'shares': 30, 'price': 120.75, 'weight': 0.08, 'sector': 'Technology'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'shares': 40, 'price': 145.30, 'weight': 0.10, 'sector': 'Consumer'},
            {'symbol': 'JPM', 'name': 'JP Morgan Chase', 'shares': 80, 'price': 155.80, 'weight': 0.09, 'sector': 'Financial'},
            {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'shares': 60, 'price': 165.20, 'weight': 0.07, 'sector': 'Healthcare'},
            {'symbol': 'V', 'name': 'Visa Inc.', 'shares': 70, 'price': 220.40, 'weight': 0.06, 'sector': 'Financial'},
            {'symbol': 'PG', 'name': 'Procter & Gamble', 'shares': 90, 'price': 155.60, 'weight': 0.05, 'sector': 'Consumer'},
            {'symbol': 'UNH', 'name': 'UnitedHealth', 'shares': 25, 'price': 480.90, 'weight': 0.04, 'sector': 'Healthcare'},
            {'symbol': 'MA', 'name': 'Mastercard', 'shares': 45, 'price': 380.20, 'weight': 0.03, 'sector': 'Financial'},
            {'symbol': 'HD', 'name': 'Home Depot', 'shares': 35, 'price': 320.50, 'weight': 0.04, 'sector': 'Consumer'},
            {'symbol': 'DIS', 'name': 'Disney', 'shares': 55, 'price': 95.30, 'weight': 0.03, 'sector': 'Consumer'},
            {'symbol': 'NVDA', 'name': 'NVIDIA', 'shares': 20, 'price': 450.80, 'weight': 0.07, 'sector': 'Technology'},
            {'symbol': 'PYPL', 'name': 'PayPal', 'shares': 65, 'price': 65.40, 'weight': 0.02, 'sector': 'Technology'},
            {'symbol': 'ADBE', 'name': 'Adobe', 'shares': 30, 'price': 520.60, 'weight': 0.05, 'sector': 'Technology'}
        ]
        
        # Calculate market values
        for holding in holdings:
            holding['market_value'] = holding['shares'] * holding['price']
            holding['cost_basis'] = holding['shares'] * (holding['price'] * np.random.uniform(0.8, 1.2))
            holding['unrealized_pnl'] = holding['market_value'] - holding['cost_basis']
            holding['unrealized_pnl_percent'] = (holding['unrealized_pnl'] / holding['cost_basis']) * 100
        
        return holdings
    
    def _calculate_holdings_breakdown(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate holdings breakdown metrics"""
        total_value = sum(holding.get('market_value', 0) for holding in holdings)
        
        breakdown = {
            'total_holdings': len(holdings),
            'total_value': total_value,
            'average_position_size': total_value / len(holdings),
            'largest_position': max(holdings, key=lambda x: x.get('market_value', 0)),
            'smallest_position': min(holdings, key=lambda x: x.get('market_value', 0)),
            'total_unrealized_pnl': sum(holding.get('unrealized_pnl', 0) for holding in holdings),
            'winners': len([h for h in holdings if h.get('unrealized_pnl', 0) > 0]),
            'losers': len([h for h in holdings if h.get('unrealized_pnl', 0) < 0])
        }
        
        return breakdown
    
    def _calculate_sector_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sector allocation"""
        sector_allocation = {}
        total_value = sum(holding.get('market_value', 0) for holding in holdings)
        
        for holding in holdings:
            sector = holding.get('sector', 'Other')
            sector_value = holding.get('market_value', 0)
            
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += sector_value / total_value
        
        return sector_allocation
    
    def _calculate_geographic_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate geographic allocation (mock implementation)"""
        # Mock geographic allocation
        return {
            'United States': 0.75,
            'Europe': 0.15,
            'Asia': 0.08,
            'Other': 0.02
        }

class RiskAnalysisWidget(BaseWidget):
    """Risk analysis widget showing portfolio risk metrics and breakdown"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            portfolio_id = self.config.data_config.get('portfolio_id', 'default_portfolio')
            
            # Get risk analysis data
            risk_data = await self._get_risk_analysis(portfolio_id)
            
            # Get risk attribution
            risk_attribution = await self._get_risk_attribution(portfolio_id)
            
            # Get VaR analysis
            var_analysis = await self._get_var_analysis(portfolio_id)
            
            risk_analysis_data = {
                'portfolio_id': portfolio_id,
                'risk_metrics': risk_data,
                'risk_attribution': risk_attribution,
                'var_analysis': var_analysis,
                'risk_assessment': self._assess_portfolio_risk(risk_data),
                'recommendations': self._generate_risk_recommendations(risk_data),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=risk_analysis_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching risk analysis data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="risk-analysis-widget" id="{self.config.widget_id}">
            <h3>Risk Analysis</h3>
            <div class="risk-metrics">
                <!-- Risk metrics will be rendered here -->
            </div>
            <div class="risk-attribution-chart">
                <!-- Risk attribution chart will be rendered here -->
            </div>
            <div class="var-analysis">
                <!-- VaR analysis will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'risk_analysis',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _get_risk_analysis(self, portfolio_id: str) -> Dict[str, Any]:
        """Get risk analysis metrics"""
        # Mock risk metrics
        return {
            'volatility': np.random.uniform(0.10, 0.25),
            'beta': np.random.uniform(0.7, 1.3),
            'var_95': np.random.uniform(0.02, 0.08),
            'var_99': np.random.uniform(0.04, 0.12),
            'sharpe_ratio': np.random.uniform(0.3, 1.5),
            'sortino_ratio': np.random.uniform(0.2, 1.2),
            'max_drawdown': np.random.uniform(0.05, 0.20),
            'calmar_ratio': np.random.uniform(0.1, 0.8),
            'tracking_error': np.random.uniform(0.02, 0.08),
            'information_ratio': np.random.uniform(0.1, 0.8)
        }
    
    async def _get_risk_attribution(self, portfolio_id: str) -> Dict[str, Any]:
        """Get risk attribution by factor"""
        # Mock risk attribution
        return {
            'market_risk': 0.65,
            'sector_risk': 0.20,
            'security_specific_risk': 0.15,
            'factor_breakdown': {
                'market_factor': 0.65,
                'size_factor': 0.08,
                'value_factor': 0.07,
                'momentum_factor': 0.05,
                'quality_factor': 0.10,
                'low_volatility_factor': 0.05
            }
        }
    
    async def _get_var_analysis(self, portfolio_id: str) -> Dict[str, Any]:
        """Get Value at Risk analysis"""
        # Mock VaR analysis
        return {
            'var_95_1day': np.random.uniform(0.01, 0.05),
            'var_95_10day': np.random.uniform(0.03, 0.15),
            'var_99_1day': np.random.uniform(0.02, 0.08),
            'var_99_10day': np.random.uniform(0.06, 0.20),
            'conditional_var': np.random.uniform(0.05, 0.15),
            'expected_shortfall': np.random.uniform(0.04, 0.12)
        }
    
    def _assess_portfolio_risk(self, risk_data: Dict[str, Any]) -> str:
        """Assess overall portfolio risk"""
        volatility = risk_data.get('volatility', 0.15)
        max_drawdown = risk_data.get('max_drawdown', 0.10)
        
        if volatility < 0.12 and max_drawdown < 0.08:
            return "Low"
        elif volatility < 0.20 and max_drawdown < 0.15:
            return "Moderate"
        else:
            return "High"
    
    def _generate_risk_recommendations(self, risk_data: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        volatility = risk_data.get('volatility', 0.15)
        max_drawdown = risk_data.get('max_drawdown', 0.10)
        sharpe_ratio = risk_data.get('sharpe_ratio', 0.8)
        
        if volatility > 0.20:
            recommendations.append("Consider reducing portfolio volatility through diversification")
        
        if max_drawdown > 0.15:
            recommendations.append("Implement downside protection strategies")
        
        if sharpe_ratio < 0.5:
            recommendations.append("Improve risk-adjusted returns through better asset allocation")
        
        if risk_data.get('beta', 1.0) > 1.2:
            recommendations.append("Consider reducing market exposure to lower systematic risk")
        
        return recommendations

class AttributionAnalysisWidget(BaseWidget):
    """Attribution analysis widget showing performance attribution breakdown"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            portfolio_id = self.config.data_config.get('portfolio_id', 'default_portfolio')
            benchmark = self.config.data_config.get('benchmark', 'SPY')
            
            # Get attribution data
            attribution_data = await self._get_attribution_analysis(portfolio_id, benchmark)
            
            # Get detailed attribution breakdown
            detailed_attribution = await self._get_detailed_attribution(portfolio_id, benchmark)
            
            # Get attribution over time
            attribution_over_time = await self._get_attribution_over_time(portfolio_id, benchmark)
            
            attribution_analysis_data = {
                'portfolio_id': portfolio_id,
                'benchmark': benchmark,
                'summary': attribution_data,
                'detailed_breakdown': detailed_attribution,
                'attribution_over_time': attribution_over_time,
                'key_drivers': self._identify_key_attribution_drivers(attribution_data),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=attribution_analysis_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching attribution analysis data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="attribution-analysis-widget" id="{self.config.widget_id}">
            <h3>Attribution Analysis</h3>
            <div class="attribution-summary">
                <!-- Attribution summary will be rendered here -->
            </div>
            <div class="attribution-waterfall">
                <!-- Attribution waterfall chart will be rendered here -->
            </div>
            <div class="sector-attribution">
                <!-- Sector attribution breakdown will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'attribution_analysis',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _get_attribution_analysis(self, portfolio_id: str, benchmark: str) -> Dict[str, Any]:
        """Get attribution analysis summary"""
        # Mock attribution data
        return {
            'total_return': 0.125,
            'benchmark_return': 0.085,
            'alpha': 0.040,
            'sector_allocation': 0.015,
            'security_selection': 0.020,
            'asset_allocation': 0.010,
            'interaction_effect': -0.005,
            'total_attribution': 0.040
        }
    
    async def _get_detailed_attribution(self, portfolio_id: str, benchmark: str) -> Dict[str, Any]:
        """Get detailed attribution breakdown"""
        # Mock detailed attribution
        return {
            'sector_attribution': {
                'Technology': 0.025,
                'Healthcare': 0.008,
                'Financial': 0.005,
                'Consumer': 0.007,
                'Industrial': -0.010,
                'Energy': -0.020
            },
            'security_selection': {
                'AAPL': 0.008,
                'MSFT': 0.006,
                'GOOGL': 0.004,
                'AMZN': -0.002,
                'TSLA': 0.004
            },
            'asset_allocation': {
                'Equities': 0.010,
                'Fixed Income': 0.005,
                'Cash': -0.005
            }
        }
    
    async def _get_attribution_over_time(self, portfolio_id: str, benchmark: str) -> List[Dict[str, Any]]:
        """Get attribution over time periods"""
        # Mock attribution over time
        periods = ['1M', '3M', '6M', '1Y', 'YTD']
        attribution_over_time = []
        
        for period in periods:
            attribution_over_time.append({
                'period': period,
                'total_return': np.random.uniform(-0.02, 0.15),
                'alpha': np.random.uniform(-0.02, 0.08),
                'sector_allocation': np.random.uniform(-0.01, 0.02),
                'security_selection': np.random.uniform(-0.01, 0.03)
            })
        
        return attribution_over_time
    
    def _identify_key_attribution_drivers(self, attribution_data: Dict[str, Any]) -> List[str]:
        """Identify key attribution drivers"""
        drivers = []
        
        sector_allocation = attribution_data.get('sector_allocation', 0)
        security_selection = attribution_data.get('security_selection', 0)
        
        if abs(sector_allocation) > 0.01:
            drivers.append(f"Sector Allocation: {sector_allocation:.2%}")
        
        if abs(security_selection) > 0.01:
            drivers.append(f"Security Selection: {security_selection:.2%}")
        
        if attribution_data.get('alpha', 0) > 0.02:
            drivers.append(f"Positive Alpha: {attribution_data['alpha']:.2%}")
        
        return drivers

class ComparisonWidget(BaseWidget):
    """Comparison widget for comparing portfolios or benchmarks"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            portfolio_ids = self.config.data_config.get('portfolio_ids', ['portfolio_1', 'portfolio_2'])
            benchmark = self.config.data_config.get('benchmark', 'SPY')
            
            # Get comparison data
            comparison_data = await self._get_portfolio_comparison(portfolio_ids, benchmark)
            
            # Get performance comparison
            performance_comparison = await self._get_performance_comparison(portfolio_ids, benchmark)
            
            # Get risk comparison
            risk_comparison = await self._get_risk_comparison(portfolio_ids, benchmark)
            
            # Get correlation analysis
            correlation_analysis = await self._get_correlation_analysis(portfolio_ids)
            
            comparison_widget_data = {
                'portfolio_ids': portfolio_ids,
                'benchmark': benchmark,
                'comparison_summary': comparison_data,
                'performance_comparison': performance_comparison,
                'risk_comparison': risk_comparison,
                'correlation_analysis': correlation_analysis,
                'ranking': self._rank_portfolios(comparison_data),
                'last_updated': datetime.now().isoformat()
            }
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=comparison_widget_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching comparison data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="comparison-widget" id="{self.config.widget_id}">
            <h3>Portfolio Comparison</h3>
            <div class="comparison-summary">
                <!-- Comparison summary will be rendered here -->
            </div>
            <div class="performance-comparison-chart">
                <!-- Performance comparison chart will be rendered here -->
            </div>
            <div class="risk-comparison-table">
                <!-- Risk comparison table will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'comparison',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _get_portfolio_comparison(self, portfolio_ids: List[str], benchmark: str) -> Dict[str, Any]:
        """Get portfolio comparison summary"""
        comparison = {}
        
        for portfolio_id in portfolio_ids:
            # Mock portfolio data
            comparison[portfolio_id] = {
                'total_return': np.random.uniform(-0.05, 0.20),
                'volatility': np.random.uniform(0.10, 0.25),
                'sharpe_ratio': np.random.uniform(0.3, 1.5),
                'max_drawdown': np.random.uniform(0.05, 0.20),
                'beta': np.random.uniform(0.7, 1.3)
            }
        
        # Add benchmark data
        comparison[benchmark] = {
            'total_return': np.random.uniform(0.05, 0.15),
            'volatility': np.random.uniform(0.12, 0.20),
            'sharpe_ratio': np.random.uniform(0.5, 1.0),
            'max_drawdown': np.random.uniform(0.08, 0.15),
            'beta': 1.0
        }
        
        return comparison
    
    async def _get_performance_comparison(self, portfolio_ids: List[str], benchmark: str) -> Dict[str, Any]:
        """Get performance comparison data"""
        # Mock performance comparison
        return {
            'periods': ['1M', '3M', '6M', '1Y'],
            'returns': {
                portfolio_id: [np.random.uniform(-0.05, 0.10) for _ in range(4)]
                for portfolio_id in portfolio_ids
            }
        }
    
    async def _get_risk_comparison(self, portfolio_ids: List[str], benchmark: str) -> Dict[str, Any]:
        """Get risk comparison data"""
        # Mock risk comparison
        return {
            'risk_metrics': {
                portfolio_id: {
                    'volatility': np.random.uniform(0.10, 0.25),
                    'var_95': np.random.uniform(0.02, 0.08),
                    'max_drawdown': np.random.uniform(0.05, 0.20)
                }
                for portfolio_id in portfolio_ids
            }
        }
    
    async def _get_correlation_analysis(self, portfolio_ids: List[str]) -> Dict[str, Any]:
        """Get correlation analysis between portfolios"""
        # Mock correlation matrix
        correlation_matrix = {}
        
        for i, portfolio_1 in enumerate(portfolio_ids):
            correlation_matrix[portfolio_1] = {}
            for j, portfolio_2 in enumerate(portfolio_ids):
                if i == j:
                    correlation_matrix[portfolio_1][portfolio_2] = 1.0
                else:
                    correlation_matrix[portfolio_1][portfolio_2] = np.random.uniform(0.3, 0.9)
        
        return correlation_matrix
    
    def _rank_portfolios(self, comparison_data: Dict[str, Any]) -> List[str]:
        """Rank portfolios by performance"""
        # Sort by Sharpe ratio
        sorted_portfolios = sorted(
            comparison_data.items(),
            key=lambda x: x[1].get('sharpe_ratio', 0),
            reverse=True
        )
        
        return [portfolio[0] for portfolio in sorted_portfolios]

# Register portfolio analytics widget templates
def register_portfolio_analytics_widgets(widget_manager):
    """Register all portfolio analytics widget templates"""
    
    widget_manager.register_template(WidgetType.PORTFOLIO_ANALYTICS, PortfolioPerformanceWidget)
    widget_manager.register_template(WidgetType.PORTFOLIO_ANALYTICS, HoldingsBreakdownWidget)
    widget_manager.register_template(WidgetType.PORTFOLIO_ANALYTICS, RiskAnalysisWidget)
    widget_manager.register_template(WidgetType.PORTFOLIO_ANALYTICS, AttributionAnalysisWidget)
    widget_manager.register_template(WidgetType.PORTFOLIO_ANALYTICS, ComparisonWidget)
