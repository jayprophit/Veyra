"""Forex Trading Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class CurrencyPair(Enum):
    EUR_USD = "EUR/USD"
    GBP_USD = "GBP/USD"
    USD_JPY = "USD/JPY"
    USD_CHF = "USD/CHF"
    AUD_USD = "AUD/USD"
    USD_CAD = "USD/CAD"
    NZD_USD = "NZD/USD"
    EUR_GBP = "EUR/GBP"
    EUR_JPY = "EUR/JPY"
    GBP_JPY = "GBP/JPY"

@dataclass
class ForexPosition:
    position_id: str
    user_id: str
    pair: str
    side: str
    size: float
    entry_price: float
    current_price: float
    pip_value: float
    unrealized_pnl: float
    margin_used: float
    leverage: float
    open_time: datetime

class ForexTrading:
    """Forex trading with margin, leverage, and cross-currency support."""
    
    def __init__(self):
        self.positions: Dict[str, ForexPosition] = {}
        self.margin_accounts: Dict[str, Dict] = {}
        self.spreads: Dict[str, float] = {
            'EUR/USD': 0.0001,
            'GBP/USD': 0.0002,
            'USD/JPY': 0.01,
            'USD/CHF': 0.0002,
            'AUD/USD': 0.0001,
            'USD/CAD': 0.0002,
            'NZD/USD': 0.0002,
            'EUR/GBP': 0.0002,
            'EUR/JPY': 0.02,
            'GBP/JPY': 0.03
        }
        self.pip_sizes: Dict[str, float] = {
            'EUR/USD': 0.0001,
            'GBP/USD': 0.0001,
            'USD/JPY': 0.01,
            'USD/CHF': 0.0001,
            'AUD/USD': 0.0001,
            'USD/CAD': 0.0001,
            'NZD/USD': 0.0001,
            'EUR/GBP': 0.0001,
            'EUR/JPY': 0.01,
            'GBP/JPY': 0.01
        }
        self.default_leverage = 50
    
    async def open_position(self,
                           user_id: str,
                           pair: str,
                           side: str,
                           size: float,
                           entry_price: float,
                           leverage: float = None) -> ForexPosition:
        """Open forex position with leverage."""
        
        position_id = f"fx_{user_id}_{datetime.now().strftime('%H%M%S%f')}"
        leverage = leverage or self.default_leverage
        
        # Calculate margin required
        notional_value = size * entry_price
        margin_used = notional_value / leverage
        
        # Get pip value
        pip_size = self.pip_sizes.get(pair, 0.0001)
        pip_value = size * pip_size
        
        position = ForexPosition(
            position_id=position_id,
            user_id=user_id,
            pair=pair,
            side=side,
            size=size,
            entry_price=entry_price,
            current_price=entry_price,
            pip_value=pip_value,
            unrealized_pnl=0.0,
            margin_used=margin_used,
            leverage=leverage,
            open_time=datetime.now()
        )
        
        self.positions[position_id] = position
        
        # Update margin account
        if user_id not in self.margin_accounts:
            self.margin_accounts[user_id] = {'balance': 10000.0, 'used_margin': 0, 'free_margin': 10000.0}
        
        self.margin_accounts[user_id]['used_margin'] += margin_used
        self.margin_accounts[user_id]['free_margin'] -= margin_used
        
        logger.info(f"Forex position opened: {position_id} {pair} {side} {size}")
        return position
    
    async def close_position(self, position_id: str, exit_price: float) -> Dict[str, Any]:
        """Close forex position."""
        if position_id not in self.positions:
            return {'error': 'Position not found'}
        
        position = self.positions[position_id]
        
        # Calculate P&L in pips and dollars
        pip_size = self.pip_sizes.get(position.pair, 0.0001)
        
        if position.side == "buy":
            pips = (exit_price - position.entry_price) / pip_size
        else:
            pips = (position.entry_price - exit_price) / pip_size
        
        realized_pnl = pips * position.pip_value
        
        # Return margin
        self.margin_accounts[position.user_id]['used_margin'] -= position.margin_used
        self.margin_accounts[position.user_id]['free_margin'] += position.margin_used + realized_pnl
        self.margin_accounts[position.user_id]['balance'] += realized_pnl
        
        del self.positions[position_id]
        
        return {
            'position_id': position_id,
            'exit_price': exit_price,
            'pips': pips,
            'realized_pnl': realized_pnl,
            'status': 'closed'
        }
    
    async def update_prices(self, prices: Dict[str, float]):
        """Update forex prices and recalculate P&L."""
        for position_id, position in self.positions.items():
            if position.pair in prices:
                position.current_price = prices[position.pair]
                
                pip_size = self.pip_sizes.get(position.pair, 0.0001)
                if position.side == "buy":
                    pips = (position.current_price - position.entry_price) / pip_size
                else:
                    pips = (position.entry_price - position.current_price) / pip_size
                
                position.unrealized_pnl = pips * position.pip_value
    
    async def calculate_margin_requirements(self, user_id: str) -> Dict[str, Any]:
        """Calculate margin requirements and levels."""
        account = self.margin_accounts.get(user_id, {'balance': 0, 'used_margin': 0, 'free_margin': 0})
        
        user_positions = [p for p in self.positions.values() if p.user_id == user_id]
        total_exposure = sum(p.size * p.current_price for p in user_positions)
        
        margin_level = (account['balance'] / account['used_margin'] * 100) if account['used_margin'] > 0 else 0
        
        return {
            'user_id': user_id,
            'balance': account['balance'],
            'used_margin': account['used_margin'],
            'free_margin': account['free_margin'],
            'margin_level_pct': margin_level,
            'total_exposure': total_exposure,
            'position_count': len(user_positions),
            'margin_call_warning': margin_level < 120,
            'stop_out_warning': margin_level < 50
        }
    
    async def get_forex_quotes(self, pairs: List[str]) -> Dict[str, Any]:
        """Get forex quotes with spreads."""
        quotes = {}
        
        for pair in pairs:
            # Simulate mid price
            import random
            base_prices = {
                'EUR/USD': 1.0850, 'GBP/USD': 1.2650, 'USD/JPY': 148.50,
                'USD/CHF': 0.8850, 'AUD/USD': 0.6550, 'USD/CAD': 1.3550,
                'NZD/USD': 0.6150, 'EUR/GBP': 0.8550, 'EUR/JPY': 162.50,
                'GBP/JPY': 190.50
            }
            
            mid = base_prices.get(pair, 1.0) + random.uniform(-0.001, 0.001)
            spread = self.spreads.get(pair, 0.0001)
            
            quotes[pair] = {
                'bid': round(mid - spread/2, 5),
                'ask': round(mid + spread/2, 5),
                'mid': round(mid, 5),
                'spread': spread,
                'spread_pips': round(spread / self.pip_sizes.get(pair, 0.0001), 1)
            }
        
        return quotes

forex_trading = ForexTrading()
