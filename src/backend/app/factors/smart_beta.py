"""Smart Beta Factor Investing Module."""
import logging
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class FactorType(Enum):
    VALUE = "value"
    MOMENTUM = "momentum"
    QUALITY = "quality"
    LOW_VOLATILITY = "low_volatility"
    SIZE = "size"
    DIVIDEND = "dividend"
    GROWTH = "growth"
    PROFITABILITY = "profitability"

@dataclass
class FactorExposure:
    factor: FactorType
    exposure: float
    z_score: float
    percentile: float

@dataclass
class SmartBetaPortfolio:
    portfolio_id: str
    name: str
    factors: List[FactorType]
    weights: Dict[str, float]
    rebalance_frequency: str
    last_rebalance: datetime

class SmartBetaEngine:
    """
    Factor-based smart beta portfolio construction and management.
    Multi-factor models for enhanced returns.
    """
    
    def __init__(self):
        self.factor_data: Dict[str, Dict[FactorType, float]] = {}
        self.portfolios: Dict[str, SmartBetaPortfolio] = {}
        self.factor_returns: Dict[FactorType, List[float]] = {f: [] for f in FactorType}
        self.factor_correlations: Dict[str, float] = {}
        
        # Factor definitions with calculation methods
        self.factor_definitions = {
            FactorType.VALUE: {
                'metrics': ['pe_ratio', 'pb_ratio', 'ps_ratio'],
                'direction': 'low',  # Lower is better
                'weight': 0.25
            },
            FactorType.MOMENTUM: {
                'metrics': ['12m_return', '6m_return', 'price_vs_52w_high'],
                'direction': 'high',
                'weight': 0.20
            },
            FactorType.QUALITY: {
                'metrics': ['roe', 'roa', 'debt_to_equity', 'earnings_quality'],
                'direction': 'high',
                'weight': 0.20
            },
            FactorType.LOW_VOLATILITY: {
                'metrics': ['volatility_1y', 'beta', 'max_drawdown'],
                'direction': 'low',
                'weight': 0.15
            },
            FactorType.SIZE: {
                'metrics': ['market_cap'],
                'direction': 'low',  # Small cap premium
                'weight': 0.10
            },
            FactorType.DIVIDEND: {
                'metrics': ['dividend_yield', 'dividend_growth', 'payout_ratio'],
                'direction': 'high',
                'weight': 0.10
            }
        }
    
    async def calculate_factor_exposures(self,
                                        symbol: str,
                                        fundamentals: Dict[str, float]) -> List[FactorExposure]:
        """Calculate factor exposures for a stock."""
        exposures = []
        
        for factor, config in self.factor_definitions.items():
            # Calculate raw factor score
            scores = []
            for metric in config['metrics']:
                if metric in fundamentals:
                    value = fundamentals[metric]
                    # Normalize (simplified)
                    scores.append(value)
            
            if scores:
                raw_score = np.mean(scores)
                
                # Calculate z-score (simplified)
                z_score = (raw_score - 0) / 1.0  # Would use historical mean/std
                
                # Calculate percentile
                percentile = 50 + z_score * 25  # Simplified conversion
                percentile = max(0, min(100, percentile))
                
                # Adjust for factor direction
                if config['direction'] == 'low':
                    z_score = -z_score
                    percentile = 100 - percentile
                
                exposures.append(FactorExposure(
                    factor=factor,
                    exposure=raw_score,
                    z_score=z_score,
                    percentile=percentile
                ))
        
        return exposures
    
    async def construct_portfolio(self,
                                 name: str,
                                 target_factors: List[str],
                                 universe: List[str],
                                 max_stocks: int = 50) -> SmartBetaPortfolio:
        """Construct smart beta portfolio based on target factors."""
        
        portfolio_id = f"sb_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}"
        
        # Score all stocks
        stock_scores = {}
        
        for symbol in universe:
            if symbol in self.factor_data:
                factor_scores = self.factor_data[symbol]
                
                # Calculate composite score
                total_score = 0
                total_weight = 0
                
                for factor_name in target_factors:
                    factor = FactorType(factor_name)
                    if factor in factor_scores:
                        weight = self.factor_definitions[factor]['weight']
                        total_score += factor_scores[factor] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    stock_scores[symbol] = total_score / total_weight
        
        # Select top stocks
        sorted_stocks = sorted(stock_scores.items(), key=lambda x: x[1], reverse=True)
        selected = sorted_stocks[:max_stocks]
        
        # Equal weight for now (could use optimization)
        weight_per_stock = 1.0 / len(selected) if selected else 0
        
        weights = {symbol: weight_per_stock for symbol, _ in selected}
        
        portfolio = SmartBetaPortfolio(
            portfolio_id=portfolio_id,
            name=name,
            factors=[FactorType(f) for f in target_factors],
            weights=weights,
            rebalance_frequency='monthly',
            last_rebalance=datetime.now()
        )
        
        self.portfolios[portfolio_id] = portfolio
        
        logger.info(f"Smart beta portfolio created: {portfolio_id} with {len(weights)} stocks")
        
        return portfolio
    
    async def get_factor_attribution(self,
                                    portfolio_id: str,
                                    start_date: str,
                                    end_date: str) -> Dict[str, Any]:
        """Get factor attribution analysis."""
        if portfolio_id not in self.portfolios:
            return {'error': 'Portfolio not found'}
        
        portfolio = self.portfolios[portfolio_id]
        
        # Calculate factor contributions (simulated)
        attribution = {}
        total_return = 0
        
        for factor in portfolio.factors:
            # Simulate factor return
            factor_return = np.random.normal(0.02, 0.05)  # 2% avg, 5% vol
            factor_contribution = factor_return * self.factor_definitions[factor]['weight']
            
            attribution[factor.value] = {
                'factor_return': round(factor_return * 100, 2),
                'weight': self.factor_definitions[factor]['weight'],
                'contribution_pct': round(factor_contribution * 100, 2)
            }
            
            total_return += factor_contribution
        
        return {
            'portfolio_id': portfolio_id,
            'period': f"{start_date} to {end_date}",
            'total_return_pct': round(total_return * 100, 2),
            'factor_attribution': attribution,
            'diversification_score': round(len(portfolio.factors) / len(FactorType) * 100, 1)
        }
    
    async def screen_by_factors(self,
                               universe: List[str],
                               factor_criteria: Dict[str, Dict],
                               max_results: int = 20) -> List[Dict]:
        """Screen stocks by factor criteria."""
        results = []
        
        for symbol in universe:
            if symbol not in self.factor_data:
                continue
            
            passes_screen = True
            factor_scores = {}
            
            for factor_name, criteria in factor_criteria.items():
                factor = FactorType(factor_name)
                
                if factor not in self.factor_data[symbol]:
                    passes_screen = False
                    break
                
                score = self.factor_data[symbol][factor]
                factor_scores[factor_name] = score
                
                # Check min threshold
                if 'min' in criteria and score < criteria['min']:
                    passes_screen = False
                    break
                
                # Check max threshold
                if 'max' in criteria and score > criteria['max']:
                    passes_screen = False
                    break
            
            if passes_screen:
                results.append({
                    'symbol': symbol,
                    'factor_scores': factor_scores,
                    'composite_score': np.mean(list(factor_scores.values()))
                })
        
        # Sort by composite score
        results.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return results[:max_results]
    
    async def get_factor_performance(self,
                                    factor: str,
                                    lookback_months: int = 12) -> Dict[str, Any]:
        """Get historical factor performance."""
        factor_type = FactorType(factor)
        
        # Simulate historical returns
        returns = np.random.normal(0.008, 0.04, lookback_months)  # Monthly returns
        
        cumulative = (1 + returns).cumprod() - 1
        
        return {
            'factor': factor,
            'lookback_months': lookback_months,
            'total_return_pct': round(cumulative[-1] * 100, 2),
            'annualized_return_pct': round(np.mean(returns) * 12 * 100, 2),
            'volatility_annual_pct': round(np.std(returns) * np.sqrt(12) * 100, 2),
            'sharpe_ratio': round(np.mean(returns) / np.std(returns) * np.sqrt(12), 2),
            'win_rate_pct': round(sum(returns > 0) / len(returns) * 100, 1),
            'monthly_returns': [round(r * 100, 2) for r in returns]
        }

smart_beta = SmartBetaEngine()
