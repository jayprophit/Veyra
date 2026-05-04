"""Trade Cost Analysis (TCA) Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class CostComponent(Enum):
    COMMISSION = "commission"
    SPREAD = "spread"
    SLIPPAGE = "slippage"
    MARKET_IMPACT = "market_impact"
    DELAY = "delay"
    OPPORTUNITY = "opportunity"

@dataclass
class TradeCost:
    component: CostComponent
    amount: float
    bps: float  # Basis points
    description: str

class TradeCostAnalysis:
    """
    Institutional-grade trade cost analysis.
    Measures explicit and implicit trading costs.
    """
    
    def __init__(self):
        self.trade_costs: Dict[str, List[TradeCost]] = {}
        self.benchmarks: Dict[str, float] = {}
        self.market_data: Dict[str, Dict] = {}
    
    async def analyze_trade(self,
                           trade_id: str,
                           symbol: str,
                           side: str,
                           quantity: float,
                           executed_price: float,
                           benchmark_price: float,
                           order_time: datetime,
                           execution_time: datetime,
                           market_conditions: Dict) -> Dict[str, Any]:
        """
        Perform full TCA on a trade.
        """
        costs = []
        total_cost = 0
        
        trade_value = quantity * executed_price
        
        # 1. Commission (explicit cost)
        commission_rate = market_conditions.get('commission_rate', 0.001)
        commission = trade_value * commission_rate
        costs.append(TradeCost(
            CostComponent.COMMISSION,
            commission,
            self._to_bps(commission, trade_value),
            "Broker commission"
        ))
        
        # 2. Spread cost
        spread = market_conditions.get('spread', 0)
        spread_cost = trade_value * (spread / executed_price) / 2  # Half spread
        costs.append(TradeCost(
            CostComponent.SPREAD,
            spread_cost,
            self._to_bps(spread_cost, trade_value),
            "Bid-ask spread"
        ))
        
        # 3. Slippage
        expected_price = market_conditions.get('arrival_price', benchmark_price)
        slippage = executed_price - expected_price if side == "buy" else expected_price - executed_price
        slippage_cost = quantity * slippage
        if slippage_cost > 0:
            costs.append(TradeCost(
                CostComponent.SLIPPAGE,
                slippage_cost,
                self._to_bps(slippage_cost, trade_value),
                "Price slippage from expected"
            ))
        
        # 4. Market impact
        pre_trade_price = market_conditions.get('pre_trade_price', benchmark_price)
        post_trade_price = market_conditions.get('post_trade_price', executed_price)
        impact = abs(post_trade_price - pre_trade_price) * quantity
        costs.append(TradeCost(
            CostComponent.MARKET_IMPACT,
            impact,
            self._to_bps(impact, trade_value),
            "Temporary market impact"
        ))
        
        # 5. Delay cost
        delay_minutes = (execution_time - order_time).total_seconds() / 60
        price_drift = market_conditions.get('price_drift_per_minute', 0)
        delay_cost = quantity * executed_price * delay_minutes * price_drift
        if delay_cost != 0:
            costs.append(TradeCost(
                CostComponent.DELAY,
                delay_cost,
                self._to_bps(delay_cost, trade_value),
                f"Delay cost ({delay_minutes:.1f} min)"
            ))
        
        # Calculate totals
        total_cost = sum(c.amount for c in costs)
        total_bps = sum(c.bps for c in costs)
        
        self.trade_costs[trade_id] = costs
        
        return {
            'trade_id': trade_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'executed_price': executed_price,
            'benchmark_price': benchmark_price,
            'trade_value': trade_value,
            'total_cost': total_cost,
            'total_bps': round(total_bps, 2),
            'cost_breakdown': [
                {
                    'component': c.component.value,
                    'amount': round(c.amount, 4),
                    'bps': round(c.bps, 2),
                    'description': c.description
                } for c in costs
            ]
        }
    
    def _to_bps(self, cost: float, trade_value: float) -> float:
        """Convert dollar cost to basis points."""
        if trade_value == 0:
            return 0
        return (cost / trade_value) * 10000
    
    async def compare_to_benchmark(self,
                                    trade_id: str,
                                    benchmark_type: str = "vwap") -> Dict[str, Any]:
        """Compare trade execution to benchmark."""
        if trade_id not in self.trade_costs:
            return {'error': 'Trade not found'}
        
        costs = self.trade_costs[trade_id]
        total_cost = sum(c.amount for c in costs)
        
        # Simulate benchmark comparison
        benchmark_costs = {
            'vwap': total_cost * 0.8,  # VWAP typically lower cost
            'twap': total_cost * 0.9,
            'arrival': total_cost * 1.1
        }
        
        benchmark = benchmark_costs.get(benchmark_type, total_cost)
        
        return {
            'trade_id': trade_id,
            'benchmark_type': benchmark_type,
            'actual_cost': total_cost,
            'benchmark_cost': benchmark,
            'difference': total_cost - benchmark,
            'outperformance': total_cost < benchmark,
            'bps_saved': self._to_bps(benchmark - total_cost, benchmark) if benchmark > 0 else 0
        }
    
    async def get_cost_summary(self,
                              user_id: str,
                              start_date: str,
                              end_date: str) -> Dict[str, Any]:
        """Get trading cost summary for period."""
        # In production: filter by user and date
        
        all_costs = []
        for costs in self.trade_costs.values():
            all_costs.extend(costs)
        
        if not all_costs:
            return {'error': 'No trade data available'}
        
        by_component = {}
        for cost in all_costs:
            component = cost.component.value
            if component not in by_component:
                by_component[component] = []
            by_component[component].append(cost.bps)
        
        summary = {
            'user_id': user_id,
            'period': f"{start_date} to {end_date}",
            'total_trades_analyzed': len(self.trade_costs),
            'cost_by_component': {
                comp: {
                    'avg_bps': round(statistics.mean(bps_list), 2),
                    'median_bps': round(statistics.median(bps_list), 2),
                    'max_bps': round(max(bps_list), 2)
                }
                for comp, bps_list in by_component.items()
            },
            'total_avg_cost_bps': round(statistics.mean(sum(c.bps for c in costs) 
                                                         for costs in self.trade_costs.values()), 2)
        }
        
        return summary

tca = TradeCostAnalysis()
