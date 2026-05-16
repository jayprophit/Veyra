"""Options Flow Analyzer - Unusual Options Activity"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptionsFlow:
    symbol: str
    strike: float
    expiration: str
    option_type: str
    volume: int
    open_interest: int
    volume_oi_ratio: float
    sentiment: str
    premium: float
    unusual: bool
    timestamp: str


class OptionsFlowAnalyzer:
    """Analyze unusual options activity"""
    
    def __init__(self):
        self.volume_threshold = 2.0  # 2x average volume
        self.oi_threshold = 1.5
    
    def analyze_chain(self, symbol: str, chain_data: List[Dict]) -> List[OptionsFlow]:
        """Analyze options chain for unusual activity"""
        flows = []
        
        for contract in chain_data:
            volume = contract.get('volume', 0)
            oi = contract.get('open_interest', 0)
            avg_volume = contract.get('avg_volume', volume)
            
            vol_oi_ratio = volume / oi if oi > 0 else 0
            
            # Determine if unusual
            is_unusual = volume > avg_volume * self.volume_threshold
            
            # Determine sentiment
            if contract.get('option_type') == 'call':
                sentiment = 'BULLISH' if contract.get('bid', 0) > contract.get('ask', 0) * 1.1 else 'NEUTRAL'
            else:
                sentiment = 'BEARISH' if contract.get('bid', 0) > contract.get('ask', 0) * 1.1 else 'NEUTRAL'
            
            flow = OptionsFlow(
                symbol=symbol,
                strike=contract.get('strike', 0),
                expiration=contract.get('expiration', ''),
                option_type=contract.get('option_type', 'call'),
                volume=volume,
                open_interest=oi,
                volume_oi_ratio=round(vol_oi_ratio, 2),
                sentiment=sentiment,
                premium=round(volume * contract.get('last_price', 0) * 100, 2),
                unusual=is_unusual,
                timestamp=datetime.now().isoformat()
            )
            flows.append(flow)
        
        return sorted(flows, key=lambda x: x.volume_oi_ratio, reverse=True)
    
    def detect_sweep(self, trades: List[Dict]) -> List[Dict]:
        """Detect options sweeps (large rapid trades)"""
        sweeps = []
        for trade in trades:
            if trade.get('size', 0) > 100 and trade.get('fill_speed', 0) < 1:
                sweeps.append({
                    'symbol': trade.get('symbol'),
                    'size': trade.get('size'),
                    'price': trade.get('price'),
                    'sentiment': 'AGGRESSIVE_BUY' if trade.get('side') == 'buy' else 'AGGRESSIVE_SELL',
                    'timestamp': trade.get('timestamp')
                })
        return sweeps
