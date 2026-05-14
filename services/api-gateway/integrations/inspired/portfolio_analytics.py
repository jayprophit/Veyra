"""
Portfolio Analytics and Attribution Module - Inspired by FactSet Recipes
Free open-source alternative using free data sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import numpy as np
from scipy import stats

from ..free.free_data_sources import get_free_data_sources_manager

logger = logging.getLogger(__name__)

@dataclass
class AttributionResult:
    portfolio_id: str
    period_start: datetime
    period_end: datetime
    total_return: float
    benchmark_return: float
    alpha: float
    sector_attribution: Dict[str, float]
    security_selection: float
    asset_allocation: float
    interaction_effect: float

@dataclass
class RiskAttribution:
    portfolio_id: str
    risk_factors: Dict[str, float]
    factor_contributions: Dict[str, float]
    specific_risk: float
    systematic_risk: float
    total_risk: float

@dataclass
class PerformanceMetrics:
    portfolio_id: str
    period_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    var_95: float
    beta: float
    tracking_error: float
    information_ratio: float

class PortfolioAnalyticsModule:
    """Portfolio analytics and attribution features inspired by FactSet recipes"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data_manager = get_free_data_sources_manager(config.get('data_sources', {}))
        self.cache = {}
        self.cache_ttl = 600  # 10 minutes
        
        logger.info("Portfolio Analytics Module initialized")
    
    async def calculate_brinson_attribution(self, portfolio_id: str, benchmark_id: str = 'SPY') -> AttributionResult:
        """
        Inspired by: "Add Brinson Attribution to a Power BI Dashboard"
        Calculate Brinson attribution for portfolio performance
        """
        try:
            # Get period dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=252)  # 1 year
            
            # Get portfolio holdings
            portfolio_holdings = await self._get_portfolio_holdings(portfolio_id)
            portfolio_weights = {h['symbol']: h['weight'] for h in portfolio_holdings}
            
            # Get benchmark holdings (S&P 500 constituents approximation)
            benchmark_weights = await self._get_benchmark_weights(benchmark_id)
            
            # Get returns for all securities
            all_symbols = list(set(portfolio_weights.keys()) | set(benchmark_weights.keys()))
            returns_data = await self._get_returns_data(all_symbols, start_date, end_date)
            
            # Calculate sector allocations
            portfolio_sectors = await self._get_sector_allocations(portfolio_weights)
            benchmark_sectors = await self._get_sector_allocations(benchmark_weights)
            
            # Calculate attribution components
            sector_attribution = self._calculate_sector_attribution(
                portfolio_weights, benchmark_weights, portfolio_sectors, benchmark_sectors, returns_data
            )
            
            security_selection = self._calculate_security_selection(
                portfolio_weights, benchmark_weights, returns_data
            )
            
            asset_allocation = self._calculate_asset_allocation(
                portfolio_sectors, benchmark_sectors, returns_data
            )
            
            interaction_effect = self._calculate_interaction_effect(
                portfolio_weights, benchmark_weights, returns_data
            )
            
            # Calculate total returns
            portfolio_return = self._calculate_portfolio_return(portfolio_weights, returns_data)
            benchmark_return = self._calculate_portfolio_return(benchmark_weights, returns_data)
            alpha = portfolio_return - benchmark_return
            
            return AttributionResult(
                portfolio_id=portfolio_id,
                period_start=start_date,
                period_end=end_date,
                total_return=portfolio_return,
                benchmark_return=benchmark_return,
                alpha=alpha,
                sector_attribution=sector_attribution,
                security_selection=security_selection,
                asset_allocation=asset_allocation,
                interaction_effect=interaction_effect
            )
            
        except Exception as e:
            logger.error(f"Error calculating Brinson attribution for {portfolio_id}: {e}")
            raise
    
    async def calculate_attribution_over_time(self, portfolio_id: str, benchmark_id: str = 'SPY') -> List[Dict[str, Any]]:
        """
        Inspired by: "Add Attribution Over Time to a Power BI Dashboard"
        Calculate attribution over multiple time periods
        """
        try:
            attribution_over_time = []
            
            # Calculate attribution for different time periods
            periods = [
                ('1M', 30),
                ('3M', 90),
                ('6M', 180),
                ('1Y', 252),
                ('YTD', (datetime.now() - datetime(datetime.now().year, 1, 1)).days)
            ]
            
            for period_name, days in periods:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Get portfolio holdings
                portfolio_holdings = await self._get_portfolio_holdings(portfolio_id)
                portfolio_weights = {h['symbol']: h['weight'] for h in portfolio_holdings}
                
                # Get benchmark weights
                benchmark_weights = await self._get_benchmark_weights(benchmark_id)
                
                # Get returns data
                all_symbols = list(set(portfolio_weights.keys()) | set(benchmark_weights.keys()))
                returns_data = await self._get_returns_data(all_symbols, start_date, end_date)
                
                # Calculate attribution
                portfolio_return = self._calculate_portfolio_return(portfolio_weights, returns_data)
                benchmark_return = self._calculate_portfolio_return(benchmark_weights, returns_data)
                
                attribution_over_time.append({
                    'period': period_name,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'portfolio_return': portfolio_return,
                    'benchmark_return': benchmark_return,
                    'alpha': portfolio_return - benchmark_return,
                    'tracking_error': self._calculate_tracking_error(portfolio_weights, benchmark_weights, returns_data),
                    'information_ratio': (portfolio_return - benchmark_return) / self._calculate_tracking_error(portfolio_weights, benchmark_weights, returns_data) if self._calculate_tracking_error(portfolio_weights, benchmark_weights, returns_data) > 0 else 0
                })
            
            return attribution_over_time
            
        except Exception as e:
            logger.error(f"Error calculating attribution over time for {portfolio_id}: {e}")
            raise
    
    async def calculate_delta_risk_attribution(self, portfolio_id: str, previous_period: str = '1M') -> Dict[str, Any]:
        """
        Inspired by: "Build an Explainable Strategy by Understanding Changes in Your Risk Attribution Calculations"
        Calculate delta risk attribution to understand changes in risk factors
        """
        try:
            # Get current and previous period dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # Current month
            prev_start_date = start_date - timedelta(days=30)  # Previous month
            
            # Get portfolio holdings for both periods
            current_holdings = await self._get_portfolio_holdings(portfolio_id)
            current_weights = {h['symbol']: h['weight'] for h in current_holdings}
            
            # Assume previous holdings (in real implementation, this would come from database)
            prev_weights = {symbol: weight * 0.95 for symbol, weight in current_weights.items()}  # Mock 5% change
            
            # Get returns data for both periods
            all_symbols = list(set(current_weights.keys()) | set(prev_weights.keys()))
            current_returns = await self._get_returns_data(all_symbols, start_date, end_date)
            prev_returns = await self._get_returns_data(all_symbols, prev_start_date, start_date)
            
            # Calculate risk metrics for both periods
            current_risk = await self._calculate_portfolio_risk(current_weights, current_returns)
            prev_risk = await self._calculate_portfolio_risk(prev_weights, prev_returns)
            
            # Calculate delta (changes) in risk factors
            delta_risk = {}
            for factor in current_risk['risk_factors']:
                current_value = current_risk['risk_factors'].get(factor, 0)
                prev_value = prev_risk['risk_factors'].get(factor, 0)
                delta_risk[factor] = {
                    'current': current_value,
                    'previous': prev_value,
                    'change': current_value - prev_value,
                    'percent_change': ((current_value - prev_value) / prev_value * 100) if prev_value != 0 else 0
                }
            
            # Calculate attribution of risk changes
            risk_attribution = {
                'weight_changes': self._calculate_weight_change_attribution(current_weights, prev_weights, current_returns),
                'volatility_changes': self._calculate_volatility_change_attribution(current_returns, prev_returns),
                'correlation_changes': self._calculate_correlation_change_attribution(current_weights, prev_weights, current_returns, prev_returns)
            }
            
            return {
                'portfolio_id': portfolio_id,
                'current_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'risk_metrics': current_risk
                },
                'previous_period': {
                    'start_date': prev_start_date.isoformat(),
                    'end_date': start_date.isoformat(),
                    'risk_metrics': prev_risk
                },
                'delta_risk_factors': delta_risk,
                'risk_attribution': risk_attribution,
                'key_drivers': self._identify_key_risk_drivers(delta_risk)
            }
            
        except Exception as e:
            logger.error(f"Error calculating delta risk attribution for {portfolio_id}: {e}")
            raise
    
    async def simulate_portfolio_strategy(self, strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspired by: "Build Confidence in Quantitative Investment Strategies with Simulated Portfolios"
        Simulate portfolio strategies with realistic backtesting
        """
        try:
            strategy_name = strategy_config.get('name', 'Strategy')
            alpha_factors = strategy_config.get('alpha_factors', [])
            universe = strategy_config.get('universe', ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])
            start_date = strategy_config.get('start_date', datetime.now() - timedelta(days=365*3))
            end_date = strategy_config.get('end_date', datetime.now())
            
            # Get historical data for universe
            historical_data = {}
            for symbol in universe:
                data = await self.data_manager.get_historical_data(symbol, start_date, end_date)
                historical_data[symbol] = data
            
            # Calculate factor scores for each security
            factor_scores = {}
            for symbol in universe:
                symbol_data = historical_data[symbol]
                factor_scores[symbol] = await self._calculate_factor_scores(symbol, symbol_data, alpha_factors)
            
            # Simulate portfolio construction
            simulation_results = []
            
            # Monthly rebalancing
            current_date = start_date
            while current_date < end_date:
                next_date = current_date + timedelta(days=30)
                
                # Select top securities based on factor scores
                selected_securities = self._select_securities_by_factors(factor_scores, top_n=10)
                
                # Calculate portfolio weights
                portfolio_weights = self._calculate_portfolio_weights(selected_securities, method='equal_weight')
                
                # Calculate portfolio performance for the period
                period_returns = await self._calculate_period_returns(portfolio_weights, historical_data, current_date, next_date)
                
                simulation_results.append({
                    'date': current_date.isoformat(),
                    'selected_securities': selected_securities,
                    'weights': portfolio_weights,
                    'period_return': period_returns,
                    'cumulative_return': self._calculate_cumulative_return(simulation_results, period_returns)
                })
                
                current_date = next_date
            
            # Calculate strategy metrics
            strategy_metrics = self._calculate_strategy_metrics(simulation_results)
            
            # Compare with benchmark
            benchmark_data = await self.data_manager.get_historical_data('SPY', start_date, end_date)
            benchmark_return = (benchmark_data[-1]['close'] - benchmark_data[0]['close']) / benchmark_data[0]['close']
            
            return {
                'strategy_name': strategy_name,
                'simulation_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_periods': len(simulation_results)
                },
                'strategy_metrics': strategy_metrics,
                'benchmark_comparison': {
                    'benchmark_return': benchmark_return,
                    'strategy_return': strategy_metrics['total_return'],
                    'alpha': strategy_metrics['total_return'] - benchmark_return,
                    'sharpe_ratio': strategy_metrics['sharpe_ratio'],
                    'max_drawdown': strategy_metrics['max_drawdown']
                },
                'monthly_results': simulation_results,
                'factor_performance': self._analyze_factor_performance(simulation_results, factor_scores)
            }
            
        except Exception as e:
            logger.error(f"Error simulating portfolio strategy: {e}")
            raise
    
    async def calculate_performance_metrics(self, portfolio_id: str, benchmark_id: str = 'SPY') -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics for a portfolio
        """
        try:
            # Get portfolio holdings
            portfolio_holdings = await self._get_portfolio_holdings(portfolio_id)
            portfolio_weights = {h['symbol']: h['weight'] for h in portfolio_holdings}
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=252)  # 1 year
            
            all_symbols = list(portfolio_weights.keys()) + [benchmark_id]
            historical_data = {}
            for symbol in all_symbols:
                data = await self.data_manager.get_historical_data(symbol, start_date, end_date)
                historical_data[symbol] = data
            
            # Calculate returns series
            portfolio_returns = self._calculate_portfolio_returns_series(portfolio_weights, historical_data)
            benchmark_returns = self._calculate_returns_series(historical_data[benchmark_id])
            
            # Calculate metrics
            period_return = portfolio_returns[-1] - portfolio_returns[0] if len(portfolio_returns) > 1 else 0
            annualized_return = (1 + period_return) ** (252 / len(portfolio_returns)) - 1 if len(portfolio_returns) > 1 else 0
            volatility = np.std(portfolio_returns) * np.sqrt(252) if len(portfolio_returns) > 1 else 0
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            max_drawdown = self._calculate_max_drawdown(portfolio_returns)
            calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
            var_95 = np.percentile(portfolio_returns, 5) if len(portfolio_returns) > 1 else 0
            
            # Calculate beta and tracking error
            beta = self._calculate_beta(portfolio_returns, benchmark_returns) if len(benchmark_returns) > 1 else 1.0
            tracking_error = self._calculate_tracking_error_series(portfolio_returns, benchmark_returns)
            information_ratio = (annualized_return - self._annualize_return(benchmark_returns)) / tracking_error if tracking_error > 0 else 0
            
            return PerformanceMetrics(
                portfolio_id=portfolio_id,
                period_return=period_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                calmar_ratio=calmar_ratio,
                var_95=var_95,
                beta=beta,
                tracking_error=tracking_error,
                information_ratio=information_ratio
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics for {portfolio_id}: {e}")
            raise
    
    async def generate_multiple_accounts_analysis(self, portfolio_ids: List[str]) -> Dict[str, Any]:
        """
        Inspired by: "Return Analytics for Multiple Accounts Inside of the Same Power BI Dashboard"
        Generate analytics for multiple portfolios in a single analysis
        """
        try:
            analysis_results = {
                'generated_at': datetime.now().isoformat(),
                'portfolios': {},
                'aggregate_analysis': {},
                'comparison_matrix': {},
                'attribution_summary': {}
            }
            
            # Calculate metrics for each portfolio
            for portfolio_id in portfolio_ids:
                metrics = await self.calculate_performance_metrics(portfolio_id)
                attribution = await self.calculate_brinson_attribution(portfolio_id)
                
                analysis_results['portfolios'][portfolio_id] = {
                    'performance_metrics': metrics,
                    'attribution': attribution
                }
            
            # Generate aggregate analysis
            all_returns = []
            all_alphas = []
            all_sharpe_ratios = []
            
            for portfolio_data in analysis_results['portfolios'].values():
                all_returns.append(portfolio_data['performance_metrics'].period_return)
                all_alphas.append(portfolio_data['attribution'].alpha)
                all_sharpe_ratios.append(portfolio_data['performance_metrics'].sharpe_ratio)
            
            analysis_results['aggregate_analysis'] = {
                'average_return': np.mean(all_returns),
                'average_alpha': np.mean(all_alphas),
                'average_sharpe_ratio': np.mean(all_sharpe_ratios),
                'best_performing_portfolio': max(analysis_results['portfolios'].keys(), 
                    key=lambda x: analysis_results['portfolios'][x]['performance_metrics'].period_return),
                'worst_performing_portfolio': min(analysis_results['portfolios'].keys(),
                    key=lambda x: analysis_results['portfolios'][x]['performance_metrics'].period_return)
            }
            
            # Generate comparison matrix
            comparison_matrix = {}
            for i, portfolio_id_1 in enumerate(portfolio_ids):
                comparison_matrix[portfolio_id_1] = {}
                for portfolio_id_2 in portfolio_ids:
                    if portfolio_id_1 != portfolio_id_2:
                        metrics_1 = analysis_results['portfolios'][portfolio_id_1]['performance_metrics']
                        metrics_2 = analysis_results['portfolios'][portfolio_id_2]['performance_metrics']
                        
                        correlation = self._calculate_portfolio_correlation(portfolio_id_1, portfolio_id_2)
                        return_diff = metrics_1.period_return - metrics_2.period_return
                        sharpe_diff = metrics_1.sharpe_ratio - metrics_2.sharpe_ratio
                        
                        comparison_matrix[portfolio_id_1][portfolio_id_2] = {
                            'correlation': correlation,
                            'return_difference': return_diff,
                            'sharpe_difference': sharpe_diff
                        }
            
            analysis_results['comparison_matrix'] = comparison_matrix
            
            # Generate attribution summary
            sector_attributions = {}
            for portfolio_id, portfolio_data in analysis_results['portfolios'].items():
                for sector, attribution in portfolio_data['attribution'].sector_attribution.items():
                    if sector not in sector_attributions:
                        sector_attributions[sector] = []
                    sector_attributions[sector].append(attribution)
            
            analysis_results['attribution_summary'] = {
                sector: {
                    'average_attribution': np.mean(attributions),
                    'best_portfolio': portfolio_ids[attributions.index(max(attributions))],
                    'worst_portfolio': portfolio_ids[attributions.index(min(attributions))]
                }
                for sector, attributions in sector_attributions.items()
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error generating multiple accounts analysis: {e}")
            raise
    
    # Helper methods
    async def _get_portfolio_holdings(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """Get portfolio holdings (mock implementation)"""
        # This would typically connect to a database
        return [
            {'symbol': 'AAPL', 'weight': 0.25, 'sector': 'Technology'},
            {'symbol': 'MSFT', 'weight': 0.20, 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'weight': 0.15, 'sector': 'Technology'},
            {'symbol': 'JPM', 'weight': 0.10, 'sector': 'Financial'},
            {'symbol': 'JNJ', 'weight': 0.10, 'sector': 'Healthcare'},
            {'symbol': 'XOM', 'weight': 0.10, 'sector': 'Energy'},
            {'symbol': 'KO', 'weight': 0.10, 'sector': 'Consumer'}
        ]
    
    async def _get_benchmark_weights(self, benchmark_id: str) -> Dict[str, float]:
        """Get benchmark weights (mock implementation)"""
        # Mock S&P 500 weights
        return {
            'AAPL': 0.07, 'MSFT': 0.06, 'GOOGL': 0.04, 'AMZN': 0.03, 'TSLA': 0.02,
            'JPM': 0.02, 'JNJ': 0.01, 'XOM': 0.01, 'KO': 0.01
        }
    
    async def _get_returns_data(self, symbols: List[str], start_date: datetime, end_date: datetime) -> Dict[str, List[float]]:
        """Get returns data for symbols"""
        returns_data = {}
        
        for symbol in symbols:
            try:
                historical_data = await self.data_manager.get_historical_data(symbol, start_date, end_date)
                if len(historical_data) > 1:
                    prices = [data['close'] for data in historical_data]
                    returns = [(prices[i] / prices[i-1] - 1) for i in range(1, len(prices))]
                    returns_data[symbol] = returns
            except Exception as e:
                logger.warning(f"Error getting returns for {symbol}: {e}")
                returns_data[symbol] = []
        
        return returns_data
    
    async def _get_sector_allocations(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Get sector allocations for weights"""
        # Mock sector mapping
        sector_mapping = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Consumer',
            'TSLA': 'Consumer', 'JPM': 'Financial', 'JNJ': 'Healthcare', 'XOM': 'Energy', 'KO': 'Consumer'
        }
        
        sector_allocations = {}
        for symbol, weight in weights.items():
            sector = sector_mapping.get(symbol, 'Other')
            sector_allocations[sector] = sector_allocations.get(sector, 0) + weight
        
        return sector_allocations
    
    def _calculate_sector_attribution(self, portfolio_weights: Dict[str, float], benchmark_weights: Dict[str, float],
                                    portfolio_sectors: Dict[str, float], benchmark_sectors: Dict[str, float],
                                    returns_data: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate sector attribution"""
        sector_attribution = {}
        
        for sector in portfolio_sectors:
            portfolio_weight = portfolio_sectors.get(sector, 0)
            benchmark_weight = benchmark_sectors.get(sector, 0)
            
            # Get sector return (weighted average of securities in sector)
            sector_return = self._calculate_sector_return(sector, portfolio_weights, returns_data)
            
            # Attribution = (Portfolio Weight - Benchmark Weight) * Sector Return
            attribution = (portfolio_weight - benchmark_weight) * sector_return
            sector_attribution[sector] = attribution
        
        return sector_attribution
    
    def _calculate_security_selection(self, portfolio_weights: Dict[str, float], benchmark_weights: Dict[str, float],
                                   returns_data: Dict[str, List[float]]) -> float:
        """Calculate security selection attribution"""
        selection_attribution = 0
        
        for symbol in portfolio_weights:
            if symbol in benchmark_weights:
                portfolio_weight = portfolio_weights[symbol]
                benchmark_weight = benchmark_weights[symbol]
                
                if symbol in returns_data and len(returns_data[symbol]) > 0:
                    security_return = np.mean(returns_data[symbol])
                    selection_attribution += (portfolio_weight - benchmark_weight) * security_return
        
        return selection_attribution
    
    def _calculate_asset_allocation(self, portfolio_sectors: Dict[str, float], benchmark_sectors: Dict[str, float],
                                  returns_data: Dict[str, List[float]]) -> float:
        """Calculate asset allocation attribution"""
        allocation_attribution = 0
        
        for sector in portfolio_sectors:
            portfolio_weight = portfolio_sectors.get(sector, 0)
            benchmark_weight = benchmark_sectors.get(sector, 0)
            
            # Use market return as sector return proxy
            sector_return = 0.08  # Mock market return
            allocation_attribution += (portfolio_weight - benchmark_weight) * sector_return
        
        return allocation_attribution
    
    def _calculate_interaction_effect(self, portfolio_weights: Dict[str, float], benchmark_weights: Dict[str, float],
                                   returns_data: Dict[str, List[float]]) -> float:
        """Calculate interaction effect"""
        # Simplified interaction effect calculation
        return 0.001  # Mock interaction effect
    
    def _calculate_portfolio_return(self, weights: Dict[str, float], returns_data: Dict[str, List[float]]) -> float:
        """Calculate portfolio return"""
        portfolio_return = 0
        
        for symbol, weight in weights.items():
            if symbol in returns_data and len(returns_data[symbol]) > 0:
                security_return = np.mean(returns_data[symbol])
                portfolio_return += weight * security_return
        
        return portfolio_return
    
    def _calculate_tracking_error(self, portfolio_weights: Dict[str, float], benchmark_weights: Dict[str, float],
                                returns_data: Dict[str, List[float]]) -> float:
        """Calculate tracking error"""
        portfolio_returns = []
        benchmark_returns = []
        
        # Calculate daily returns for both portfolios
        for i in range(max(len(returns_data.get(next(iter(portfolio_weights), ''), [])), 
                        len(returns_data.get(next(iter(benchmark_weights), ''), [])))):
            portfolio_daily_return = 0
            benchmark_daily_return = 0
            
            for symbol, weight in portfolio_weights.items():
                if symbol in returns_data and i < len(returns_data[symbol]):
                    portfolio_daily_return += weight * returns_data[symbol][i]
            
            for symbol, weight in benchmark_weights.items():
                if symbol in returns_data and i < len(returns_data[symbol]):
                    benchmark_daily_return += weight * returns_data[symbol][i]
            
            portfolio_returns.append(portfolio_daily_return)
            benchmark_returns.append(benchmark_daily_return)
        
        # Calculate tracking error (standard deviation of differences)
        if len(portfolio_returns) > 1 and len(benchmark_returns) > 1:
            differences = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
            return np.std(differences) * np.sqrt(252)
        
        return 0.1  # Default tracking error
    
    async def _calculate_portfolio_risk(self, weights: Dict[str, float], returns_data: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        # Mock risk calculation
        return {
            'risk_factors': {
                'market': 0.8,
                'size': 0.3,
                'value': 0.2,
                'momentum': 0.1,
                'quality': 0.4
            },
            'factor_contributions': {
                'market': 0.06,
                'size': 0.02,
                'value': 0.01,
                'momentum': 0.005,
                'quality': 0.015
            },
            'specific_risk': 0.04,
            'systematic_risk': 0.11,
            'total_risk': 0.15
        }
    
    def _calculate_weight_change_attribution(self, current_weights: Dict[str, float], prev_weights: Dict[str, float],
                                          returns_data: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate attribution from weight changes"""
        attribution = {}
        
        for symbol in current_weights:
            current_weight = current_weights.get(symbol, 0)
            prev_weight = prev_weights.get(symbol, 0)
            weight_change = current_weight - prev_weight
            
            if symbol in returns_data and len(returns_data[symbol]) > 0:
                avg_return = np.mean(returns_data[symbol])
                attribution[symbol] = weight_change * avg_return
        
        return attribution
    
    def _calculate_volatility_change_attribution(self, current_returns: Dict[str, List[float]], 
                                              prev_returns: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate attribution from volatility changes"""
        attribution = {}
        
        for symbol in current_returns:
            if symbol in prev_returns:
                current_vol = np.std(current_returns[symbol]) if len(current_returns[symbol]) > 1 else 0
                prev_vol = np.std(prev_returns[symbol]) if len(prev_returns[symbol]) > 1 else 0
                vol_change = current_vol - prev_vol
                
                # Mock attribution calculation
                attribution[symbol] = vol_change * 0.1  # Simplified
        
        return attribution
    
    def _calculate_correlation_change_attribution(self, current_weights: Dict[str, float], prev_weights: Dict[str, float],
                                                current_returns: Dict[str, List[float]], prev_returns: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate attribution from correlation changes"""
        # Simplified correlation change attribution
        return {'correlation_change': 0.005}
    
    def _identify_key_risk_drivers(self, delta_risk: Dict[str, Any]) -> List[str]:
        """Identify key drivers of risk changes"""
        key_drivers = []
        
        for factor, data in delta_risk.items():
            if abs(data.get('percent_change', 0)) > 10:  # 10% threshold
                key_drivers.append(factor)
        
        return key_drivers
    
    async def _calculate_factor_scores(self, symbol: str, historical_data: List[Dict[str, Any]], 
                                     alpha_factors: List[str]) -> Dict[str, float]:
        """Calculate factor scores for a security"""
        scores = {}
        
        if len(historical_data) < 20:
            return {factor: 0.5 for factor in alpha_factors}
        
        prices = [data['close'] for data in historical_data]
        volumes = [data['volume'] for data in historical_data]
        
        # Calculate basic factors
        if 'momentum' in alpha_factors:
            # 12-month momentum
            if len(prices) >= 252:
                momentum = (prices[-1] - prices[-252]) / prices[-252]
                scores['momentum'] = momentum
            else:
                scores['momentum'] = 0
        
        if 'mean_reversion' in alpha_factors:
            # Short-term mean reversion
            if len(prices) >= 20:
                ma20 = np.mean(prices[-20:])
                mean_reversion = (ma20 - prices[-1]) / ma20
                scores['mean_reversion'] = mean_reversion
            else:
                scores['mean_reversion'] = 0
        
        if 'volume' in alpha_factors:
            # Volume factor
            if len(volumes) >= 20:
                avg_volume = np.mean(volumes[-20:])
                volume_factor = volumes[-1] / avg_volume
                scores['volume'] = volume_factor
            else:
                scores['volume'] = 1
        
        # Default scores for missing factors
        for factor in alpha_factors:
            if factor not in scores:
                scores[factor] = 0.5
        
        return scores
    
    def _select_securities_by_factors(self, factor_scores: Dict[str, Dict[str, float]], top_n: int = 10) -> List[str]:
        """Select top securities based on factor scores"""
        # Calculate composite score
        composite_scores = {}
        
        for symbol, scores in factor_scores.items():
            # Simple average of all factor scores
            composite_score = np.mean(list(scores.values())) if scores else 0
            composite_scores[symbol] = composite_score
        
        # Sort by composite score and select top N
        sorted_securities = sorted(composite_scores.items(), key=lambda x: x[1], reverse=True)
        return [symbol for symbol, score in sorted_securities[:top_n]]
    
    def _calculate_portfolio_weights(self, selected_securities: List[str], method: str = 'equal_weight') -> Dict[str, float]:
        """Calculate portfolio weights"""
        if method == 'equal_weight':
            weight = 1.0 / len(selected_securities)
            return {symbol: weight for symbol in selected_securities}
        elif method == 'market_cap_weighted':
            # Mock market cap weights
            return {symbol: 1.0 / len(selected_securities) for symbol in selected_securities}
        else:
            return {symbol: 1.0 / len(selected_securities) for symbol in selected_securities}
    
    async def _calculate_period_returns(self, weights: Dict[str, float], historical_data: Dict[str, List[Dict[str, Any]]],
                                      start_date: datetime, end_date: datetime) -> float:
        """Calculate portfolio returns for a period"""
        period_return = 0
        
        for symbol, weight in weights.items():
            if symbol in historical_data:
                symbol_data = historical_data[symbol]
                if len(symbol_data) >= 2:
                    start_price = symbol_data[0]['close']
                    end_price = symbol_data[-1]['close']
                    security_return = (end_price - start_price) / start_price
                    period_return += weight * security_return
        
        return period_return
    
    def _calculate_cumulative_return(self, simulation_results: List[Dict[str, Any]], current_period_return: float) -> float:
        """Calculate cumulative return"""
        if not simulation_results:
            return current_period_return
        
        last_cumulative = simulation_results[-1].get('cumulative_return', 0)
        return (1 + last_cumulative) * (1 + current_period_return) - 1
    
    def _calculate_strategy_metrics(self, simulation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate strategy performance metrics"""
        if not simulation_results:
            return {}
        
        period_returns = [result['period_return'] for result in simulation_results]
        cumulative_returns = [result['cumulative_return'] for result in simulation_results]
        
        total_return = cumulative_returns[-1] if cumulative_returns else 0
        volatility = np.std(period_returns) * np.sqrt(12) if len(period_returns) > 1 else 0
        sharpe_ratio = (total_return / len(simulation_results) * 12) / volatility if volatility > 0 else 0
        
        # Calculate max drawdown
        peak = cumulative_returns[0]
        max_drawdown = 0
        for cum_return in cumulative_returns:
            if cum_return > peak:
                peak = cum_return
            drawdown = (peak - cum_return) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            'total_return': total_return,
            'annualized_return': total_return / len(simulation_results) * 12,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': len([r for r in period_returns if r > 0]) / len(period_returns),
            'average_return': np.mean(period_returns),
            'best_month': max(period_returns),
            'worst_month': min(period_returns)
        }
    
    def _analyze_factor_performance(self, simulation_results: List[Dict[str, Any]], factor_scores: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyze factor performance"""
        # Simplified factor performance analysis
        return {
            'momentum_performance': 0.08,
            'mean_reversion_performance': 0.05,
            'volume_performance': 0.03,
            'factor_turnover': 0.2
        }
    
    def _calculate_portfolio_returns_series(self, weights: Dict[str, float], historical_data: Dict[str, List[Dict[str, Any]]]) -> List[float]:
        """Calculate portfolio returns series"""
        if not historical_data:
            return []
        
        # Find the minimum length across all securities
        min_length = min(len(data) for data in historical_data.values())
        
        portfolio_returns = []
        for i in range(1, min_length):
            daily_return = 0
            for symbol, weight in weights.items():
                if symbol in historical_data and i < len(historical_data[symbol]):
                    prev_price = historical_data[symbol][i-1]['close']
                    curr_price = historical_data[symbol][i]['close']
                    security_return = (curr_price - prev_price) / prev_price
                    daily_return += weight * security_return
            
            portfolio_returns.append(daily_return)
        
        return portfolio_returns
    
    def _calculate_returns_series(self, historical_data: List[Dict[str, Any]]) -> List[float]:
        """Calculate returns series from historical data"""
        if len(historical_data) < 2:
            return []
        
        returns = []
        for i in range(1, len(historical_data)):
            prev_price = historical_data[i-1]['close']
            curr_price = historical_data[i]['close']
            returns.append((curr_price - prev_price) / prev_price)
        
        return returns
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0
        
        cumulative_returns = [1]
        for ret in returns:
            cumulative_returns.append(cumulative_returns[-1] * (1 + ret))
        
        peak = cumulative_returns[0]
        max_drawdown = 0
        
        for cum_return in cumulative_returns:
            if cum_return > peak:
                peak = cum_return
            drawdown = (peak - cum_return) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_beta(self, portfolio_returns: List[float], benchmark_returns: List[float]) -> float:
        """Calculate beta"""
        if len(portfolio_returns) < 2 or len(benchmark_returns) < 2:
            return 1.0
        
        # Align returns
        min_length = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_aligned = portfolio_returns[:min_length]
        benchmark_aligned = benchmark_returns[:min_length]
        
        if min_length < 2:
            return 1.0
        
        # Calculate beta using covariance
        covariance = np.cov(portfolio_aligned, benchmark_aligned)[0, 1]
        benchmark_variance = np.var(benchmark_aligned)
        
        return covariance / benchmark_variance if benchmark_variance > 0 else 1.0
    
    def _calculate_tracking_error_series(self, portfolio_returns: List[float], benchmark_returns: List[float]) -> float:
        """Calculate tracking error from returns series"""
        if len(portfolio_returns) < 2 or len(benchmark_returns) < 2:
            return 0.1
        
        # Align returns
        min_length = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_aligned = portfolio_returns[:min_length]
        benchmark_aligned = benchmark_returns[:min_length]
        
        if min_length < 2:
            return 0.1
        
        # Calculate tracking error
        differences = [p - b for p, b in zip(portfolio_aligned, benchmark_aligned)]
        return np.std(differences) * np.sqrt(252)
    
    def _annualize_return(self, returns: List[float]) -> float:
        """Annualize return"""
        if not returns:
            return 0
        
        total_return = (1 + np.mean(returns)) ** 252 - 1
        return total_return
    
    def _calculate_portfolio_correlation(self, portfolio_id_1: str, portfolio_id_2: str) -> float:
        """Calculate correlation between two portfolios"""
        # Mock correlation calculation
        return 0.7
    
    def _calculate_sector_return(self, sector: str, weights: Dict[str, float], returns_data: Dict[str, List[float]]) -> float:
        """Calculate sector return"""
        sector_return = 0
        sector_weight = 0
        
        # Mock sector mapping
        sector_mapping = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Consumer',
            'TSLA': 'Consumer', 'JPM': 'Financial', 'JNJ': 'Healthcare', 'XOM': 'Energy', 'KO': 'Consumer'
        }
        
        for symbol, weight in weights.items():
            if sector_mapping.get(symbol) == sector and symbol in returns_data:
                if len(returns_data[symbol]) > 0:
                    security_return = np.mean(returns_data[symbol])
                    sector_return += weight * security_return
                    sector_weight += weight
        
        return sector_return if sector_weight > 0 else 0.08  # Default sector return

# Factory function
def get_portfolio_analytics_module(config: Dict[str, Any] = None) -> PortfolioAnalyticsModule:
    """Factory function to get portfolio analytics module"""
    return PortfolioAnalyticsModule(config)
