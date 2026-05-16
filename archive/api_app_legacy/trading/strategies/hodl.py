"""
HODL Strategy with Dynamic Thresholds
Buy on dips, sell on significant gains
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio

@dataclass
class HODLPosition:
    symbol: str
    entry_price: float
    quantity: float
    buy_threshold: float  # % drop to buy more
    sell_threshold: float  # % gain to sell
    highest_price: float  # For trailing stop
    created_at: datetime

class HODLStrategy:
    """
    HODL (Hold On for Dear Life) with smart buy/sell thresholds
    - Buy more when price drops (dips)
    - Sell when significant gains reached
    - Trailing stop to lock in profits
    """
    
    def __init__(self,
                 default_buy_threshold: float = -5.0,  # Buy 5% dip
                 default_sell_threshold: float = 15.0,  # Sell at 15% gain
                 trailing_stop_pct: float = 10.0):  # Sell if drops 10% from peak
        self.default_buy_threshold = default_buy_threshold
        self.default_sell_threshold = default_sell_threshold
        self.trailing_stop_pct = trailing_stop_pct
        
        self.positions: Dict[str, HODLPosition] = {}
        self.active = False
        self.trade_history: List[Dict] = []
    
    def open_position(self, 
                      symbol: str, 
                      entry_price: float, 
                      quantity: float,
                      buy_threshold: Optional[float] = None,
                      sell_threshold: Optional[float] = None) -> HODLPosition:
        """Open a new HODL position"""
        position = HODLPosition(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            buy_threshold=buy_threshold or self.default_buy_threshold,
            sell_threshold=sell_threshold or self.default_sell_threshold,
            highest_price=entry_price,
            created_at=datetime.now()
        )
        self.positions[symbol] = position
        return position
    
    def check_buy_opportunity(self, symbol: str, current_price: float) -> Optional[Dict]:
        """Check if we should buy more (averaging down)"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        price_drop_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        
        # Check if price dropped enough to buy more
        if price_drop_pct <= position.buy_threshold:
            return {
                'action': 'buy_more',
                'symbol': symbol,
                'current_price': current_price,
                'entry_price': position.entry_price,
                'drop_pct': round(price_drop_pct, 2),
                'threshold': position.buy_threshold,
                'reason': f'Price dropped {abs(price_drop_pct):.1f}% - buying opportunity'
            }
        
        return None
    
    def check_sell_signal(self, symbol: str, current_price: float) -> Optional[Dict]:
        """Check if we should sell (profit target or trailing stop)"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        # Update highest price
        if current_price > position.highest_price:
            position.highest_price = current_price
        
        # Calculate gains
        gain_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        drop_from_peak_pct = ((position.highest_price - current_price) / position.highest_price) * 100
        
        # Check profit target
        if gain_pct >= position.sell_threshold:
            return {
                'action': 'sell',
                'symbol': symbol,
                'current_price': current_price,
                'entry_price': position.entry_price,
                'gain_pct': round(gain_pct, 2),
                'threshold': position.sell_threshold,
                'reason': f'Profit target reached: {gain_pct:.1f}% gain',
                'type': 'profit_target'
            }
        
        # Check trailing stop
        if drop_from_peak_pct >= self.trailing_stop_pct and gain_pct > 0:
            return {
                'action': 'sell',
                'symbol': symbol,
                'current_price': current_price,
                'entry_price': position.entry_price,
                'gain_pct': round(gain_pct, 2),
                'drop_from_peak': round(drop_from_peak_pct, 2),
                'reason': f'Trailing stop triggered: dropped {drop_from_peak_pct:.1f}% from peak',
                'type': 'trailing_stop'
            }
        
        return None
    
    async def monitor_positions(self, price_provider, check_interval: int = 60):
        """Monitor all positions for buy/sell signals"""
        self.active = True
        
        while self.active:
            try:
                for symbol in list(self.positions.keys()):
                    try:
                        current_price = await price_provider.get_price(symbol)
                        
                        # Check buy opportunity
                        buy_signal = self.check_buy_opportunity(symbol, current_price)
                        if buy_signal:
                            print(f"HODL Buy Signal: {buy_signal['reason']}")
                        
                        # Check sell signal
                        sell_signal = self.check_sell_signal(symbol, current_price)
                        if sell_signal:
                            print(f"HODL Sell Signal: {sell_signal['reason']}")
                    
                    except Exception as e:
                        print(f"Error monitoring {symbol}: {e}")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"HODL monitor error: {e}")
                await asyncio.sleep(check_interval)
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[Dict]:
        """Close a HODL position"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        gain_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
        profit = (exit_price - position.entry_price) * position.quantity
        
        trade_record = {
            'symbol': symbol,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'quantity': position.quantity,
            'gain_pct': round(gain_pct, 2),
            'profit': round(profit, 2),
            'holding_days': (datetime.now() - position.created_at).days,
            'closed_at': datetime.now().isoformat()
        }
        
        self.trade_history.append(trade_record)
        del self.positions[symbol]
        
        return trade_record
    
    def get_position_summary(self, symbol: str, current_price: float) -> Optional[Dict]:
        """Get summary of a position"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        gain_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        unrealized_pnl = (current_price - position.entry_price) * position.quantity
        
        return {
            'symbol': symbol,
            'entry_price': position.entry_price,
            'current_price': current_price,
            'quantity': position.quantity,
            'gain_pct': round(gain_pct, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'highest_price': position.highest_price,
            'buy_threshold': position.buy_threshold,
            'sell_threshold': position.sell_threshold,
            'holding_days': (datetime.now() - position.created_at).days
        }
    
    def stop(self):
        """Stop monitoring"""
        self.active = False
    
    def get_all_positions(self, price_provider) -> List[Dict]:
        """Get summary of all positions"""
        summaries = []
        for symbol in self.positions:
            try:
                # In async context, would await price
                summary = {
                    'symbol': symbol,
                    'entry_price': self.positions[symbol].entry_price,
                    'quantity': self.positions[symbol].quantity,
                    'holding_days': (datetime.now() - self.positions[symbol].created_at).days
                }
                summaries.append(summary)
            except Exception as e:
                print(f"Error getting position for {symbol}: {e}")
        
        return summaries
