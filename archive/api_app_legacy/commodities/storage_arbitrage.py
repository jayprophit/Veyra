"""
Commodity Storage Arbitrage
===========================
Analyze commodity storage arbitrage opportunities
Contango/backwardation, storage costs, convenience yield
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np


@dataclass
class FuturesCurve:
    commodity: str
    spot_price: float
    forward_prices: Dict[str, float]  # month -> price
    storage_cost_monthly: float
    convenience_yield: float


class CommodityStorageArbitrage:
    """
    Analyze commodity storage arbitrage opportunities
    
    When futures curve is in contango (upward sloping),
    storage may be profitable
    """
    
    # Storage costs by commodity (per unit per month)
    STORAGE_COSTS = {
        'crude_oil': {'per_barrel_per_month': 0.50, 'unit': 'barrel'},
        'gasoline': {'per_barrel_per_month': 0.60, 'unit': 'barrel'},
        'natural_gas': {'per_mmbtu_per_month': 0.10, 'unit': 'mmbtu'},
        'copper': {'per_tonne_per_month': 15, 'unit': 'tonne'},
        'aluminum': {'per_tonne_per_month': 8, 'unit': 'tonne'},
        'wheat': {'per_bushel_per_month': 0.08, 'unit': 'bushel'},
        'corn': {'per_bushel_per_month': 0.06, 'unit': 'bushel'},
        'soybeans': {'per_bushel_per_month': 0.07, 'unit': 'bushel'},
        'gold': {'per_oz_per_month': 0.05, 'unit': 'oz'},  # Very low
        'silver': {'per_oz_per_month': 0.002, 'unit': 'oz'}
    }
    
    def analyze_storage_arbitrage(self, curve: FuturesCurve,
                                  storage_months: int = 6) -> Dict:
        """
        Analyze storage arbitrage opportunity
        
        Profit = (Future Price - Spot) - Storage Costs - Opportunity Cost
        """
        
        spot = curve.spot_price
        
        # Get forward price for target month
        target_month = f"M{storage_months}"
        if target_month not in curve.forward_prices:
            # Use furthest available
            target_month = max(curve.forward_prices.keys(), 
                             key=lambda x: int(x.replace('M', '')) if x.startswith('M') else 0)
        
        forward = curve.forward_prices[target_month]
        
        # Gross spread
        gross_spread = forward - spot
        
        # Storage costs
        storage_cost_total = curve.storage_cost_monthly * storage_months
        
        # Opportunity cost (cost of capital)
        opportunity_cost = spot * 0.05 * (storage_months / 12)  # 5% annual
        
        # Convenience yield (benefit of holding physical)
        convenience_benefit = spot * curve.convenience_yield * (storage_months / 12)
        
        # Net profit
        total_costs = storage_cost_total + opportunity_cost - convenience_benefit
        net_profit = gross_spread - total_costs
        
        # Annualized return
        if net_profit > 0 and spot > 0:
            annualized_return = (net_profit / spot) * (12 / storage_months) * 100
        else:
            annualized_return = 0
        
        # Curve shape
        curve_shape = self._analyze_curve_shape(curve)
        
        return {
            'commodity': curve.commodity,
            'spot_price': spot,
            'forward_price': forward,
            'storage_months': storage_months,
            'gross_spread': round(gross_spread, 2),
            'storage_costs': round(storage_cost_total, 2),
            'opportunity_cost': round(opportunity_cost, 2),
            'convenience_yield_benefit': round(convenience_benefit, 2),
            'total_costs': round(total_costs, 2),
            'net_profit': round(net_profit, 2),
            'annualized_return_pct': round(annualized_return, 1),
            'curve_shape': curve_shape,
            'arbitrage_viable': net_profit > 0,
            'recommendation': 'STORE' if net_profit > 0 else 'NO_ARBITRAGE'
        }
    
    def _analyze_curve_shape(self, curve: FuturesCurve) -> str:
        """Analyze futures curve shape"""
        forward_prices = list(curve.forward_prices.values())
        
        if len(forward_prices) < 2:
            return 'INSUFFICIENT_DATA'
        
        # Check if curve slopes up (contango) or down (backwardation)
        first = forward_prices[0]
        last = forward_prices[-1]
        
        if last > first * 1.02:
            return 'CONTANGO (storage favorable)'
        elif last < first * 0.98:
            return 'BACKWARDATION (storage unfavorable)'
        else:
            return 'FLAT (no clear signal)'
    
    def find_best_storage_opportunities(self, 
                                        curves: List[FuturesCurve]) -> List[Dict]:
        """Find best storage arbitrage opportunities across commodities"""
        
        opportunities = []
        
        for curve in curves:
            # Test 3, 6, 12 month storage
            for months in [3, 6, 12]:
                analysis = self.analyze_storage_arbitrage(curve, months)
                
                if analysis['arbitrage_viable']:
                    opportunities.append({
                        'commodity': curve.commodity,
                        'months': months,
                        'net_profit': analysis['net_profit'],
                        'annualized_return': analysis['annualized_return_pct'],
                        'spot': analysis['spot_price']
                    })
        
        # Sort by annualized return
        opportunities.sort(key=lambda x: x['annualized_return'], reverse=True)
        
        return opportunities[:10]  # Top 10
    
    def get_commodity_storage_guide(self, commodity: str) -> Dict:
        """Get storage guide for specific commodity"""
        
        guides = {
            'crude_oil': {
                'storage_types': ['Tank farms', 'Floating storage', 'Salt caverns'],
                'typical_duration': '1-6 months',
                'seasonal_patterns': 'Build inventory in fall, draw in summer',
                'risks': ['Contamination', 'Evaporation', 'Price volatility'],
                'returns_annual': '5-15% when contango steep'
            },
            'natural_gas': {
                'storage_types': ['Depleted reservoirs', 'Salt caverns', 'LNG tanks'],
                'typical_duration': 'Seasonal (6 months)',
                'seasonal_patterns': 'Store summer, sell winter',
                'risks': ['Weather risk', 'Pipeline constraints', 'Demand spikes'],
                'returns_annual': '10-30% seasonal arbitrage'
            },
            'metals': {
                'storage_types': ['LME warehouses', 'Private vaults'],
                'typical_duration': 'Long-term (contango carry)',
                'seasonal_patterns': 'Limited seasonality',
                'risks': ['Warehouse queues', 'Financing costs', 'Base rate changes'],
                'returns_annual': '3-8% carry returns'
            },
            'grains': {
                'storage_types': ['Silo', 'Warehouse', 'On-farm'],
                'typical_duration': 'Harvest to pre-planting',
                'seasonal_patterns': 'Store post-harvest, sell before new crop',
                'risks': ['Spoilage', 'Moisture', 'Price decline'],
                'returns_annual': 'Variable, basis arbitrage'
            }
        }
        
        return guides.get(commodity, {'error': f'No guide for {commodity}'})


# Usage
def check_storage_arb(commodity: str, spot: float, 
                     forward_6m: float, storage_monthly: float,
                     convenience: float = 0.02) -> Dict:
    """Quick storage arbitrage check"""
    
    analyzer = CommodityStorageArbitrage()
    
    curve = FuturesCurve(
        commodity=commodity,
        spot_price=spot,
        forward_prices={'M6': forward_6m},
        storage_cost_monthly=storage_monthly,
        convenience_yield=convenience
    )
    
    return analyzer.analyze_storage_arbitrage(curve, 6)


def find_best_storage_opps(curves_data: List[Dict]) -> List[Dict]:
    """Find best storage opportunities"""
    analyzer = CommodityStorageArbitrage()
    
    curves = [
        FuturesCurve(
            commodity=c['name'],
            spot_price=c['spot'],
            forward_prices=c['forwards'],
            storage_cost_monthly=c['storage'],
            convenience_yield=c.get('convenience', 0.02)
        )
        for c in curves_data
    ]
    
    return analyzer.find_best_storage_opportunities(curves)


def get_storage_guide(commodity: str) -> Dict:
    """Get commodity storage guide"""
    analyzer = CommodityStorageArbitrage()
    return analyzer.get_commodity_storage_guide(commodity)
