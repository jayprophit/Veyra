"""Perpetual Futures Trading Module"""
from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import datetime

@dataclass
class PerpetualPosition:
    symbol: str
    side: str
    size: float
    entry_price: float
    leverage: float
    liquidation_price: float
    unrealized_pnl: float

class PerpetualFuturesTrader:
    """Trade perpetual futures with funding rate awareness."""
    
    async def get_funding_rate(self, symbol: str) -> Dict[str, Any]:
        return {'symbol': symbol, 'funding_rate': 0.0001, 'next_funding': '08:00:00'}
    
    async def open_position(self, user_id: str, symbol: str, side: str, size: float, leverage: float) -> Dict[str, Any]:
        margin = size / leverage
        return {'position_id': 'pos_001', 'margin_required': margin, 'liquidation_price': 40000 if side == 'long' else 60000}
    
    async def close_position(self, position_id: str) -> Dict[str, Any]:
        return {'position_id': position_id, 'closed': True, 'realized_pnl': 150.50}
    
    async def get_liquidation_risk(self, user_id: str) -> List[Dict]:
        return [{'symbol': 'BTC-PERP', 'risk_level': 'medium', 'distance_to_liq': 15.2}]
