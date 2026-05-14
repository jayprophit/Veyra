"""Options Flow Analyzer - Unusual Activity Detection"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

class OptionsFlowAnalyzer:
    """
    Detect unusual options activity for trading signals
    
    Features:
    - Unusual volume detection
    - Large block trades (whales)
    - Put/Call ratio extremes
    - Sweep detection (multiple exchanges)
    - Premium analysis
    """
    
    def __init__(self):
        self.volume_threshold = 2.0  # 2x average volume
        self.premium_threshold = 100000  # $100K minimum
        self.history: Dict[str, List[Dict]] = {}
    
    def analyze_flow(self, options_data: List[Dict]) -> List[Dict]:
        """
        Analyze options flow for unusual activity
        
        Args:
            options_data: List of option trades with
                {ticker, strike, expiry, type, volume, premium, sentiment}
        """
        signals = []
        
        for trade in options_data:
            ticker = trade.get('ticker')
            volume = trade.get('volume', 0)
            premium = trade.get('premium', 0)
            
            # Calculate metrics
            avg_volume = self._get_average_volume(ticker)
            volume_ratio = volume / avg_volume if avg_volume > 0 else 0
            
            # Check for unusual activity
            is_unusual = (
                volume_ratio > self.volume_threshold or
                premium > self.premium_threshold
            )
            
            if is_unusual:
                signal = self._classify_trade(trade, volume_ratio)
                if signal:
                    signals.append(signal)
            
            # Store for history
            if ticker not in self.history:
                self.history[ticker] = []
            self.history[ticker].append(trade)
        
        return signals
    
    def _get_average_volume(self, ticker: str) -> float:
        """Get average options volume for ticker"""
        history = self.history.get(ticker, [])
        if not history:
            return 100  # Default baseline
        
        volumes = [h.get('volume', 0) for h in history[-20:]]  # Last 20 trades
        return np.mean(volumes) if volumes else 100
    
    def _classify_trade(self, trade: Dict, volume_ratio: float) -> Optional[Dict]:
        """Classify unusual trade into signal category"""
        option_type = trade.get('type', '').upper()
        sentiment = trade.get('sentiment', 'neutral')
        premium = trade.get('premium', 0)
        
        # Whale trade (very large)
        if premium > 500000:
            category = 'WHALE_BLOCK'
            confidence = 0.85
        elif volume_ratio > 5:
            category = 'VOLUME_SPIKE'
            confidence = 0.75
        elif sentiment in ['bullish', 'bearish']:
            category = 'DIRECTIONAL_BET'
            confidence = 0.70
        else:
            category = 'UNUSUAL_ACTIVITY'
            confidence = 0.60
        
        # Determine direction
        if option_type == 'CALL':
            if sentiment == 'bullish':
                direction = 'BULLISH'
            else:
                direction = 'NEUTRAL'
        elif option_type == 'PUT':
            if sentiment == 'bearish':
                direction = 'BEARISH'
            else:
                direction = 'NEUTRAL'  # Could be hedge
        else:
            direction = 'NEUTRAL'
        
        return {
            'ticker': trade.get('ticker'),
            'signal_type': category,
            'direction': direction,
            'option_type': option_type,
            'strike': trade.get('strike'),
            'expiry': trade.get('expiry'),
            'volume': trade.get('volume'),
            'premium_usd': premium,
            'volume_ratio': round(volume_ratio, 2),
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_put_call_ratio(self, ticker: str, window: int = 5) -> Dict:
        """Calculate put/call ratio for ticker"""
        history = self.history.get(ticker, [])
        
        if not history:
            return {'ratio': 1.0, 'sentiment': 'neutral'}
        
        recent = history[-window:]
        
        puts = sum(1 for h in recent if h.get('type', '').upper() == 'PUT')
        calls = sum(1 for h in recent if h.get('type', '').upper() == 'CALL')
        
        ratio = puts / calls if calls > 0 else 1.0
        
        # Interpret ratio
        if ratio > 1.2:
            sentiment = 'bearish'
        elif ratio < 0.8:
            sentiment = 'bullish'
        else:
            sentiment = 'neutral'
        
        return {
            'ticker': ticker,
            'put_call_ratio': round(ratio, 2),
            'sentiment': sentiment,
            'puts_count': puts,
            'calls_count': calls,
            'extreme_reading': ratio > 1.5 or ratio < 0.5
        }
    
    def scan_for_whales(self, min_premium: float = 1000000) -> List[Dict]:
        """Find whale trades above premium threshold"""
        whales = []
        
        for ticker, trades in self.history.items():
            for trade in trades:
                if trade.get('premium', 0) >= min_premium:
                    whales.append({
                        'ticker': ticker,
                        'premium': trade.get('premium'),
                        'type': trade.get('type'),
                        'strike': trade.get('strike'),
                        'expiry': trade.get('expiry')
                    })
        
        return sorted(whales, key=lambda x: x['premium'], reverse=True)[:20]

# Quick usage
def detect_unusual_options(options_trades: List[Dict]) -> List[Dict]:
    """Quick unusual options detection"""
    analyzer = OptionsFlowAnalyzer()
    return analyzer.analyze_flow(options_trades)
