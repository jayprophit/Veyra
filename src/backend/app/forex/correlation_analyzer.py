"""
Forex Correlation Analyzer
==========================
Analyze currency correlations, cointegration, and arbitrage opportunities
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ForexCorrelationAnalyzer:
    """
    Analyze forex pair correlations and relationships
    
    Features:
    - Pair correlation matrices
    - Cointegration testing
    - Triangular arbitrage detection
    - Carry trade analysis
    - Volatility clustering
    """
    
    MAJOR_PAIRS = ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 
                   'AUDUSD', 'USDCAD', 'NZDUSD']
    
    def __init__(self):
        self.price_data = {}
        self.correlation_matrix = None
        self.returns_data = None
    
    def load_price_data(self, prices_df: pd.DataFrame):
        """Load forex price data"""
        self.price_data = prices_df
        self.returns_data = prices_df.pct_change().dropna()
        logger.info(f"Loaded price data for {len(prices_df.columns)} pairs")
    
    def calculate_correlation_matrix(self, window: int = 60) -> pd.DataFrame:
        """Calculate rolling correlation matrix"""
        if self.returns_data is None:
            raise ValueError("Load price data first")
        
        if len(self.returns_data) < window:
            window = len(self.returns_data)
        
        recent_returns = self.returns_data.tail(window)
        corr_matrix = recent_returns.corr()
        
        self.correlation_matrix = corr_matrix
        return corr_matrix
    
    def find_high_correlations(self, threshold: float = 0.8) -> List[Dict]:
        """Find highly correlated pairs"""
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        high_corr = []
        
        pairs = self.correlation_matrix.columns
        
        for i in range(len(pairs)):
            for j in range(i + 1, len(pairs)):
                corr = self.correlation_matrix.iloc[i, j]
                
                if abs(corr) > threshold:
                    high_corr.append({
                        'pair1': pairs[i],
                        'pair2': pairs[j],
                        'correlation': round(corr, 4),
                        'relationship': 'strong_positive' if corr > 0 else 'strong_negative'
                    })
        
        # Sort by absolute correlation
        high_corr.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return high_corr
    
    def detect_triangular_arbitrage(self, 
                                   rates: Dict[str, float]) -> List[Dict]:
        """
        Detect triangular arbitrage opportunities
        
        Example: EUR -> USD -> JPY -> EUR
        If (EURUSD * USDJPY) != EURJPY, arbitrage exists
        """
        opportunities = []
        
        # Check EUR -> USD -> JPY -> EUR
        if 'EURUSD' in rates and 'USDJPY' in rates:
            implied_eurjpy = rates['EURUSD'] * rates['USDJPY']
            
            if 'EURJPY' in rates:
                actual_eurjpy = rates['EURJPY']
                spread = abs(implied_eurjpy - actual_eurjpy) / actual_eurjpy
                
                if spread > 0.001:  # 10 pips
                    opportunities.append({
                        'triangle': 'EUR-USD-JPY',
                        'path': 'EUR -> USD -> JPY -> EUR',
                        'implied_rate': round(implied_eurjpy, 5),
                        'actual_rate': round(actual_eurjpy, 5),
                        'spread_pct': round(spread * 100, 4),
                        'profit_potential': round(spread * 10000, 1)  # In pips
                    }}
        
        # Check GBP -> USD -> JPY -> GBP
        if 'GBPUSD' in rates and 'USDJPY' in rates:
            implied_gbpjpy = rates['GBPUSD'] * rates['USDJPY']
            
            if 'GBPJPY' in rates:
                actual_gbpjpy = rates['GBPJPY']
                spread = abs(implied_gbpjpy - actual_gbpjpy) / actual_gbpjpy
                
                if spread > 0.001:
                    opportunities.append({
                        'triangle': 'GBP-USD-JPY',
                        'path': 'GBP -> USD -> JPY -> GBP',
                        'implied_rate': round(implied_gbpjpy, 3),
                        'actual_rate': round(actual_gbpjpy, 3),
                        'spread_pct': round(spread * 100, 4),
                        'profit_potential': round(spread * 10000, 1)
                    })
        
        # Check AUD -> USD -> CAD -> AUD
        if 'AUDUSD' in rates and 'USDCAD' in rates:
            implied_audcad = rates['AUDUSD'] * rates['USDCAD']
            
            if 'AUDCAD' in rates:
                actual_audcad = rates['AUDCAD']
                spread = abs(implied_audcad - actual_audcad) / actual_audcad
                
                if spread > 0.001:
                    opportunities.append({
                        'triangle': 'AUD-USD-CAD',
                        'path': 'AUD -> USD -> CAD -> AUD',
                        'implied_rate': round(implied_audcad, 5),
                        'actual_rate': round(actual_audcad, 5),
                        'spread_pct': round(spread * 100, 4),
                        'profit_potential': round(spread * 10000, 1)
                    })
        
        return opportunities
    
    def analyze_carry_trade(self, 
                           rates: Dict[str, float],
                           interest_rates: Dict[str, float]) -> List[Dict]:
        """
        Analyze carry trade opportunities
        
        Borrow low-yielding currency, invest in high-yielding currency
        """
        opportunities = []
        
        for base_ccy, base_rate in interest_rates.items():
            for quote_ccy, quote_rate in interest_rates.items():
                if base_ccy != quote_ccy:
                    # Calculate interest rate differential
                    differential = quote_rate - base_rate
                    
                    # Get exchange rate
                    pair = f"{base_ccy}{quote_ccy}"
                    if pair in rates:
                        spot = rates[pair]
                        
                        # Annualized carry return
                        carry_return = differential
                        
                        # Simple risk estimate (volatility proxy)
                        risk_score = 5 if abs(differential) < 2 else 7
                        
                        if differential > 2.0:  # >2% differential
                            opportunities.append({
                                'trade': f"Long {quote_ccy}, Short {base_ccy}",
                                'pair': pair,
                                'spot_rate': spot,
                                'yield_differential': round(differential, 2),
                                'annual_return_pct': round(carry_return, 2),
                                'risk_score': risk_score,
                                'risk_adjusted_return': round(carry_return / risk_score, 2),
                                'recommendation': 'ATTRACTIVE' if differential > 4 else 'MODERATE'
                            })
        
        # Sort by risk-adjusted return
        opportunities.sort(key=lambda x: x['risk_adjusted_return'], reverse=True)
        
        return opportunities[:10]
    
    def calculate_atr(self, pair: str, period: int = 14) -> float:
        """Calculate Average True Range for volatility"""
        if self.price_data is None or pair not in self.price_data.columns:
            return 0.0
        
        prices = self.price_data[pair]
        
        # Calculate daily ranges
        high_low = prices.rolling(window=2).max() - prices.rolling(window=2).min()
        
        # ATR is average of these ranges
        atr = high_low.rolling(window=period).mean().iloc[-1]
        
        return atr if not np.isnan(atr) else 0.0
    
    def get_volatility_ranking(self) -> List[Dict]:
        """Rank pairs by volatility (ATR)"""
        if self.price_data is None:
            return []
        
        volatilities = []
        
        for pair in self.price_data.columns:
            atr = self.calculate_atr(pair)
            current_price = self.price_data[pair].iloc[-1]
            
            # Normalize ATR as percentage of price
            atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
            
            volatilities.append({
                'pair': pair,
                'atr': round(atr, 5),
                'atr_pct': round(atr_pct, 3),
                'current_price': round(current_price, 5),
                'volatility_rank': 'HIGH' if atr_pct > 1.0 else 'MEDIUM' if atr_pct > 0.5 else 'LOW'
            })
        
        # Sort by ATR percentage
        volatilities.sort(key=lambda x: x['atr_pct'], reverse=True)
        
        return volatilities
    
    def generate_forex_report(self) -> Dict:
        """Generate comprehensive forex analysis report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'correlations': {
                'matrix': self.correlation_matrix.to_dict() if self.correlation_matrix is not None else {},
                'strongest': self.find_high_correlations(0.8)[:5]
            },
            'volatility': {
                'ranking': self.get_volatility_ranking()[:5]
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate trading recommendations based on analysis"""
        recommendations = []
        
        # Check for high correlations (diversification concern)
        high_corr = self.find_high_correlations(0.9)
        if len(high_corr) > 3:
            recommendations.append(
                "High correlation environment detected. Consider reducing position sizes."
            )
        
        # Volatility warning
        vol_ranking = self.get_volatility_ranking()
        if vol_ranking and vol_ranking[0]['atr_pct'] > 2.0:
            recommendations.append(
                f"High volatility in {vol_ranking[0]['pair']}. Use wider stops."
            )
        
        if not recommendations:
            recommendations.append("Normal market conditions. Standard risk management applies.")
        
        return recommendations


# Usage
def analyze_forex_correlations(price_df: pd.DataFrame) -> Dict:
    """Quick forex correlation analysis"""
    analyzer = ForexCorrelationAnalyzer()
    analyzer.load_price_data(price_df)
    
    return {
        'correlation_matrix': analyzer.calculate_correlation_matrix().to_dict(),
        'high_correlations': analyzer.find_high_correlations(0.8),
        'volatility_ranking': analyzer.get_volatility_ranking()[:10]
    }


def find_triangular_arbitrage(rates: Dict[str, float]) -> List[Dict]:
    """Quick triangular arbitrage detection"""
    analyzer = ForexCorrelationAnalyzer()
    return analyzer.detect_triangular_arbitrage(rates)


def get_carry_trades(rates: Dict[str, float], 
                     interest_rates: Dict[str, float]) -> List[Dict]:
    """Get carry trade opportunities"""
    analyzer = ForexCorrelationAnalyzer()
    return analyzer.analyze_carry_trade(rates, interest_rates)
