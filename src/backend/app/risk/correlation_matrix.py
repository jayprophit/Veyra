"""Correlation Matrix - Asset Relationship Analysis"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CorrelationPair:
    asset_1: str
    asset_2: str
    correlation: float
    beta: float
    relationship: str


class CorrelationMatrix:
    """Asset correlation and beta analysis"""
    
    def __init__(self):
        self.lookback = 252  # 1 year of daily data
    
    def calculate(
        self,
        returns: pd.DataFrame,
        benchmark: Optional[str] = None
    ) -> Dict:
        """Calculate full correlation matrix"""
        
        corr_matrix = returns.corr()
        
        # Calculate betas against benchmark
        betas = {}
        if benchmark and benchmark in returns.columns:
            benchmark_var = returns[benchmark].var()
            for col in returns.columns:
                if col != benchmark:
                    covariance = returns[col].cov(returns[benchmark])
                    betas[col] = covariance / benchmark_var if benchmark_var > 0 else 0
        
        # Find highest/lowest correlations
        pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                asset_1 = corr_matrix.columns[i]
                asset_2 = corr_matrix.columns[j]
                corr = corr_matrix.iloc[i, j]
                
                relationship = self._classify_relationship(corr)
                
                pairs.append(CorrelationPair(
                    asset_1=asset_1,
                    asset_2=asset_2,
                    correlation=round(corr, 4),
                    beta=round(betas.get(asset_1, 0), 4),
                    relationship=relationship
                ))
        
        return {
            'matrix': corr_matrix.to_dict(),
            'pairs': sorted(pairs, key=lambda x: abs(x.correlation), reverse=True),
            'betas': betas,
            'highest_correlation': max(pairs, key=lambda x: x.correlation),
            'lowest_correlation': min(pairs, key=lambda x: x.correlation),
            'diversification_score': self._diversification_score(corr_matrix)
        }
    
    def _classify_relationship(self, corr: float) -> str:
        """Classify correlation strength"""
        if abs(corr) < 0.3:
            return "WEAK"
        elif abs(corr) < 0.7:
            return "MODERATE"
        else:
            return "STRONG"
    
    def _diversification_score(self, corr_matrix: pd.DataFrame) -> float:
        """Calculate portfolio diversification score (0-100)"""
        # Lower average correlation = better diversification
        avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
        # Score: 100 = perfect diversification (avg_corr = -1), 0 = no diversification (avg_corr = 1)
        score = (1 - avg_corr) / 2 * 100
        return round(score, 2)
    
    def find_diversifiers(
        self,
        target_symbol: str,
        universe: pd.DataFrame,
        min_correlation: float = 0.3
    ) -> List[str]:
        """Find assets with low correlation to target"""
        corrs = universe.corrwith(universe[target_symbol])
        diversifiers = corrs[abs(corrs) < min_correlation].index.tolist()
        return [d for d in diversifiers if d != target_symbol]
