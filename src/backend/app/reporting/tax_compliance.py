"""Tax Reporting and Compliance Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class TradeRecord:
    trade_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: datetime
    fees: float
    exchange: str
    realized_pnl: Optional[float] = None
    holding_period_days: Optional[int] = None

class TaxCompliance:
    """Automated tax reporting with FIFO/LIFO accounting."""
    
    def __init__(self):
        self.trades: Dict[str, List[TradeRecord]] = defaultdict(list)
        self.cost_basis: Dict[str, List[tuple]] = defaultdict(list)  # (qty, price, date)
    
    async def record_trade(self, user_id: str, trade: Dict) -> str:
        """Record trade for tax purposes."""
        record = TradeRecord(
            trade_id=trade['id'],
            symbol=trade['symbol'],
            side=trade['side'],
            quantity=trade['quantity'],
            price=trade['price'],
            timestamp=trade.get('timestamp', datetime.now()),
            fees=trade.get('fees', 0),
            exchange=trade.get('exchange', 'default')
        )
        
        # Calculate realized P&L using FIFO
        if trade['side'] == 'sell':
            record.realized_pnl = await self._calculate_realized_pnl(
                user_id, trade['symbol'], trade['quantity'], trade['price']
            )
            record.holding_period_days = await self._calculate_holding_period(
                user_id, trade['symbol'], trade['quantity']
            )
        
        self.trades[user_id].append(record)
        
        # Update cost basis
        if trade['side'] == 'buy':
            self.cost_basis[user_id].append((
                trade['symbol'], trade['quantity'], trade['price'], record.timestamp
            ))
        
        return record.trade_id
    
    async def _calculate_realized_pnl(self, user_id: str, symbol: str, 
                                       sell_qty: float, sell_price: float) -> float:
        """Calculate realized P&L using FIFO method."""
        total_pnl = 0
        remaining_qty = sell_qty
        
        # Filter buys for this symbol
        buys = [(qty, price, date) for s, qty, price, date in self.cost_basis[user_id] 
                if s == symbol]
        
        for qty, price, date in buys:
            if remaining_qty <= 0:
                break
            
            used_qty = min(qty, remaining_qty)
            pnl = used_qty * (sell_price - price)
            total_pnl += pnl
            remaining_qty -= used_qty
        
        return total_pnl
    
    async def _calculate_holding_period(self, user_id: str, symbol: str, 
                                        qty: float) -> int:
        """Calculate average holding period in days."""
        buys = [(q, d) for s, q, p, d in self.cost_basis[user_id] if s == symbol]
        
        if not buys:
            return 0
        
        # Use oldest buy date (FIFO)
        oldest_date = min([d for q, d in buys])
        days = (datetime.now() - oldest_date).days
        return max(days, 1)
    
    async def generate_tax_report(self, user_id: str, year: int, 
                                  method: str = "fifo") -> Dict[str, Any]:
        """Generate annual tax report."""
        trades = [t for t in self.trades[user_id] 
                  if t.timestamp.year == year]
        
        # Categorize by holding period
        short_term = [t for t in trades if t.holding_period_days and t.holding_period_days <= 365]
        long_term = [t for t in trades if t.holding_period_days and t.holding_period_days > 365]
        
        short_term_gains = sum(t.realized_pnl for t in short_term if t.realized_pnl)
        long_term_gains = sum(t.realized_pnl for t in long_term if t.realized_pnl)
        
        total_fees = sum(t.fees for t in trades)
        
        # Group by symbol
        symbol_summary = defaultdict(lambda: {'trades': 0, 'pnl': 0, 'volume': 0})
        for t in trades:
            symbol_summary[t.symbol]['trades'] += 1
            symbol_summary[t.symbol]['pnl'] += (t.realized_pnl or 0)
            symbol_summary[t.symbol]['volume'] += t.quantity * t.price
        
        return {
            'year': year,
            'user_id': user_id,
            'accounting_method': method,
            'total_trades': len(trades),
            'short_term_gains': short_term_gains,
            'long_term_gains': long_term_gains,
            'total_realized_pnl': short_term_gains + long_term_gains,
            'total_fees': total_fees,
            'net_taxable_gains': short_term_gains + long_term_gains - total_fees,
            'symbol_breakdown': dict(symbol_summary),
            'generated_at': datetime.now().isoformat()
        }
    
    async def get_unrealized_gains(self, user_id: str, 
                                   current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Calculate unrealized gains based on current prices."""
        unrealized = {}
        
        for symbol, current_price in current_prices.items():
            # Get remaining position
            buys = [(qty, price) for s, qty, price, date in self.cost_basis[user_id] if s == symbol]
            total_qty = sum(qty for qty, price in buys)
            avg_cost = sum(qty * price for qty, price in buys) / total_qty if total_qty > 0 else 0
            
            if total_qty > 0:
                unrealized_pnl = total_qty * (current_price - avg_cost)
                unrealized[symbol] = {
                    'quantity': total_qty,
                    'avg_cost': avg_cost,
                    'current_price': current_price,
                    'unrealized_pnl': unrealized_pnl,
                    'return_pct': ((current_price - avg_cost) / avg_cost) * 100 if avg_cost > 0 else 0
                }
        
        return {
            'user_id': user_id,
            'positions': unrealized,
            'total_unrealized_pnl': sum(p['unrealized_pnl'] for p in unrealized.values())
        }

tax_compliance = TaxCompliance()
