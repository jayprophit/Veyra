"""Portfolio Rebalancing Engine."""
import logging
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class RebalanceFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    THRESHOLD = "threshold"

@dataclass
class TargetAllocation:
    symbol: str
    target_weight: float
    min_weight: float
    max_weight: float
    drift_tolerance: float

class PortfolioRebalancer:
    """Automated portfolio rebalancing with tax efficiency."""
    
    def __init__(self):
        self.portfolios: Dict[str, Dict] = {}
        self.rebalance_history: List[Dict] = []
        self.tax_loss_harvesting = True
        self.min_trade_size = 100
    
    async def create_rebalance_plan(self,
                                   user_id: str,
                                   target_allocations: List[Dict],
                                   current_holdings: Dict[str, float],
                                   current_prices: Dict[str, float],
                                   total_value: float) -> Dict[str, Any]:
        """Create rebalancing plan to reach target allocations."""
        
        # Calculate current weights
        current_weights = {}
        for symbol, quantity in current_holdings.items():
            price = current_prices.get(symbol, 0)
            value = quantity * price
            current_weights[symbol] = value / total_value if total_value > 0 else 0
        
        # Calculate target trades
        trades = []
        total_tax_impact = 0
        
        for target in target_allocations:
            symbol = target['symbol']
            target_weight = target['target_weight']
            drift_tolerance = target.get('drift_tolerance', 0.05)
            
            target_value = total_value * target_weight
            current_value = total_value * current_weights.get(symbol, 0)
            diff_value = target_value - current_value
            
            if abs(diff_value) < self.min_trade_size:
                continue
            
            current_weight = current_weights.get(symbol, 0)
            drift = abs(current_weight - target_weight)
            
            if drift <= drift_tolerance:
                continue
            
            price = current_prices.get(symbol, 0)
            if price == 0:
                continue
            
            quantity = diff_value / price
            side = "buy" if diff_value > 0 else "sell"
            tax_impact = 0 if side == "buy" else self._estimate_tax_impact(symbol, abs(quantity), price)
            total_tax_impact += tax_impact
            
            trades.append({
                'symbol': symbol,
                'side': side,
                'quantity': abs(quantity),
                'estimated_value': abs(diff_value),
                'current_weight': current_weight,
                'target_weight': target_weight,
                'drift': drift,
                'estimated_tax_impact': tax_impact
            })
        
        trades.sort(key=lambda x: (0 if x['side'] == 'sell' else 1, -x['drift']))
        
        return {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'total_value': total_value,
            'trades': trades,
            'trade_count': len(trades),
            'estimated_tax_impact': total_tax_impact,
            'estimated_commission': len(trades) * 5
        }
    
    def _estimate_tax_impact(self, symbol: str, quantity: float, price: float) -> float:
        assumed_cost_basis = price * 0.9
        gain = (price - assumed_cost_basis) * quantity
        return max(0, gain * 0.20)
    
    async def check_drift(self,
                         user_id: str,
                         target_allocations: List[Dict],
                         current_holdings: Dict[str, float],
                         current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Check portfolio drift from targets."""
        
        total_value = sum(
            current_holdings.get(sym, 0) * current_prices.get(sym, 0)
            for sym in set(list(current_holdings.keys()) + [t['symbol'] for t in target_allocations])
        )
        
        drift_analysis = []
        max_drift = 0
        needs_rebalance = False
        
        for target in target_allocations:
            symbol = target['symbol']
            current_qty = current_holdings.get(symbol, 0)
            current_value = current_qty * current_prices.get(symbol, 0)
            current_weight = current_value / total_value if total_value > 0 else 0
            
            drift = abs(current_weight - target['target_weight'])
            max_drift = max(max_drift, drift)
            
            if drift > target.get('drift_tolerance', 0.05):
                needs_rebalance = True
            
            drift_analysis.append({
                'symbol': symbol,
                'target_weight': target['target_weight'],
                'current_weight': current_weight,
                'drift': drift,
                'drift_pct': drift * 100,
                'within_tolerance': drift <= target.get('drift_tolerance', 0.05),
                'action_needed': 'rebalance' if drift > target.get('drift_tolerance', 0.05) else 'hold'
            })
        
        return {
            'user_id': user_id,
            'total_value': total_value,
            'max_drift': max_drift,
            'max_drift_pct': max_drift * 100,
            'needs_rebalance': needs_rebalance,
            'drift_by_asset': drift_analysis,
            'checked_at': datetime.now().isoformat()
        }

rebalancer = PortfolioRebalancer()
