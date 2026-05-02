"""
Deep Supply Chain Arbitrage Analyzer
======================================
Comprehensive supply chain analysis for arbitrage opportunities
Port congestion, shipping rates, inventory timing, geographic arbitrage
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import numpy as np


class ArbitrageType(Enum):
    GEOGRAPHIC = "geographic"  # Buy in cheap market, sell in expensive
    TEMPORAL = "temporal"  # Store and sell later when prices rise
    LOGISTICS = "logistics"  # Route optimization savings
    CURRENCY = "currency"  # FX rate differences


@dataclass
class SupplyRoute:
    origin: str
    destination: str
    mode: str  # 'sea', 'air', 'rail', 'truck'
    cost_per_ton: float
    duration_days: int
    reliability_score: float  # 0-1
    current_capacity: str  # 'available', 'limited', 'full'


class DeepSupplyChainAnalyzer:
    """
    Deep supply chain analysis for commodity and product arbitrage
    
    Tracks:
    - Global shipping routes and rates
    - Port congestion levels
    - Inventory positioning
    - Regional price differentials
    """
    
    # Major commodity trade routes
    TRADE_ROUTES = {
        'iron_ore': {
            'australia_china': {'distance_nm': 3500, 'typical_rate': 15},  # Capesize
            'brazil_china': {'distance_nm': 10500, 'typical_rate': 25},
        },
        'crude_oil': {
            'middle_east_asia': {'distance_nm': 6500, 'typical_rate': 12},
            'us_gulf_asia': {'distance_nm': 16000, 'typical_rate': 28},
            'north_sea_europe': {'distance_nm': 500, 'typical_rate': 5},
        },
        'lng': {
            'us_gulf_europe': {'distance_nm': 4800, 'typical_rate': 80000},  # per day
            'qatar_asia': {'distance_nm': 6500, 'typical_rate': 75000},
            'australia_asia': {'distance_nm': 4500, 'typical_rate': 70000},
        },
        'grains': {
            'us_gulf_china': {'distance_nm': 14000, 'typical_rate': 45},
            'black_sea_china': {'distance_nm': 8500, 'typical_rate': 35},
            'brazil_china': {'distance_nm': 10500, 'typical_rate': 38},
        }
    }
    
    # Port congestion index (0-100, higher = more congested)
    PORT_CONGESTION = {
        'los_angeles': 75,
        'long_beach': 70,
        'shanghai': 65,
        'ningbo': 60,
        'shenzhen': 55,
        'rotterdam': 40,
        'hamburg': 35,
        'antwerp': 30,
        'singapore': 50,
        'busan': 45,
        'mumbai': 80,
        'santos': 55,
        'dubai': 40
    }
    
    def find_geographic_arbitrage(self, commodity: str,
                                   price_by_region: Dict[str, float]) -> List[Dict]:
        """
        Find geographic arbitrage opportunities
        
        Buy in low-price region, sell in high-price region
        Account for transportation costs
        """
        opportunities = []
        
        regions = list(price_by_region.keys())
        
        for i, origin in enumerate(regions):
            for destination in regions[i+1:]:
                origin_price = price_by_region[origin]
                dest_price = price_by_region[destination]
                
                # Calculate price differential
                price_diff = dest_price - origin_price
                
                # Estimate transport cost
                transport_cost = self._estimate_transport_cost(
                    commodity, origin, destination
                )
                
                # Net arbitrage profit
                net_profit = price_diff - transport_cost
                
                if net_profit > 0:
                    # Check route reliability
                    route = self._get_route_info(origin, destination)
                    
                    opportunities.append({
                        'origin': origin,
                        'destination': destination,
                        'commodity': commodity,
                        'buy_price': origin_price,
                        'sell_price': dest_price,
                        'gross_spread': round(price_diff, 2),
                        'transport_cost': round(transport_cost, 2),
                        'net_profit_per_unit': round(net_profit, 2),
                        'profit_margin_pct': round(net_profit / origin_price * 100, 1),
                        'route_reliability': route.get('reliability', 0.8),
                        'transit_days': route.get('duration', 30),
                        'risk_factors': self._assess_route_risks(origin, destination)
                    })
        
        # Sort by profit margin
        opportunities.sort(key=lambda x: x['net_profit_per_unit'], reverse=True)
        
        return opportunities
    
    def _estimate_transport_cost(self, commodity: str, 
                                  origin: str, destination: str) -> float:
        """Estimate transportation cost per unit"""
        
        # Base ocean freight rates per ton
        base_rates = {
            'iron_ore': 15,
            'crude_oil': 10,
            'grains': 40,
            'coal': 20,
            'lng': 0.5  # per mmbtu equivalent
        }
        
        base = base_rates.get(commodity, 25)
        
        # Distance multiplier
        distance_mult = 1.0
        if any(x in origin.lower() for x in ['brazil', 'us']):
            if any(x in destination.lower() for x in ['china', 'asia']):
                distance_mult = 1.5
        
        # Port congestion impact
        congestion = max(
            self.PORT_CONGESTION.get(origin.lower().replace(' ', '_'), 50),
            self.PORT_CONGESTION.get(destination.lower().replace(' ', '_'), 50)
        )
        congestion_premium = 1 + (congestion - 50) / 100
        
        return base * distance_mult * congestion_premium
    
    def _get_route_info(self, origin: str, destination: str) -> Dict:
        """Get route information"""
        # Simplified route database
        routes = {
            ('us', 'china'): {'duration': 25, 'reliability': 0.85},
            ('brazil', 'china'): {'duration': 35, 'reliability': 0.80},
            ('australia', 'china'): {'duration': 15, 'reliability': 0.90},
            ('middle_east', 'asia'): {'duration': 20, 'reliability': 0.88},
            ('europe', 'us'): {'duration': 12, 'reliability': 0.92},
        }
        
        # Find matching route
        for (o_key, d_key), info in routes.items():
            if o_key in origin.lower() or o_key in destination.lower():
                if d_key in destination.lower() or d_key in origin.lower():
                    return info
        
        return {'duration': 30, 'reliability': 0.75}
    
    def _assess_route_risks(self, origin: str, destination: str) -> List[str]:
        """Assess risks for trade route"""
        risks = []
        
        # Check port congestion
        if self.PORT_CONGESTION.get(origin.lower().replace(' ', '_'), 0) > 70:
            risks.append('High origin port congestion')
        if self.PORT_CONGESTION.get(destination.lower().replace(' ', '_'), 0) > 70:
            risks.append('High destination port congestion')
        
        # Geopolitical chokepoints
        chokepoint_routes = [
            ('middle_east', 'asia'),
            ('europe', 'asia')
        ]
        
        for o, d in chokepoint_routes:
            if o in origin.lower() or o in destination.lower():
                if d in destination.lower() or d in origin.lower():
                    risks.append('Strait of Hormuz/Malacca chokepoint risk')
        
        return risks if risks else ['Standard route risks']
    
    def analyze_temporal_storage(self, commodity: str,
                                  current_price: float,
                                  storage_cost_monthly: float,
                                  forward_prices: Dict[str, float],
                                  storage_duration_months: int = 6) -> Dict:
        """
        Analyze temporal arbitrage via storage
        
        Store commodity now, sell at higher future price
        """
        
        # Find best forward price within storage period
        best_month = None
        best_price = current_price
        
        for month_str, price in forward_prices.items():
            # Parse month
            try:
                month = int(month_str)
                if month <= storage_duration_months and price > best_price:
                    best_price = price
                    best_month = month
            except:
                continue
        
        # Calculate costs
        total_storage_cost = storage_cost_monthly * (best_month or storage_duration_months)
        opportunity_cost = current_price * 0.05 * (best_month or storage_duration_months) / 12  # 5% annual cost of capital
        
        total_costs = total_storage_cost + opportunity_cost
        
        # Profit calculation
        gross_profit = best_price - current_price
        net_profit = gross_profit - total_costs
        
        return {
            'commodity': commodity,
            'current_price': current_price,
            'target_sale_price': best_price,
            'storage_months': best_month or storage_duration_months,
            'gross_spread': round(gross_profit, 2),
            'storage_cost': round(total_storage_cost, 2),
            'opportunity_cost': round(opportunity_cost, 2),
            'total_costs': round(total_costs, 2),
            'net_profit': round(net_profit, 2),
            'annualized_return_pct': round(
                (net_profit / current_price) * (12 / (best_month or storage_duration_months)) * 100, 1
            ) if net_profit > 0 else 0,
            'viable': net_profit > 0
        }
    
    def get_port_congestion_report(self) -> Dict:
        """Get global port congestion status"""
        
        # Categorize ports
        high_congestion = {k: v for k, v in self.PORT_CONGESTION.items() if v >= 70}
        medium_congestion = {k: v for k, v in self.PORT_CONGESTION.items() if 50 <= v < 70}
        normal = {k: v for k, v in self.PORT_CONGESTION.items() if v < 50}
        
        avg_congestion = np.mean(list(self.PORT_CONGESTION.values()))
        
        return {
            'average_congestion_index': round(avg_congestion, 1),
            'status': 'CRITICAL' if avg_congestion > 70 else 'ELEVATED' if avg_congestion > 55 else 'NORMAL',
            'high_congestion_ports': len(high_congestion),
            'medium_congestion_ports': len(medium_congestion),
            'normal_ports': len(normal),
            'top_congested': sorted(
                self.PORT_CONGESTION.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            'impact': {
                'shipping_delays': f"+{int((avg_congestion - 40) / 2)} days average" if avg_congestion > 40 else 'Normal',
                'freight_cost_premium': f"+{int((avg_congestion - 40))}%" if avg_congestion > 40 else 'Normal',
                'inventory_holding_cost': 'Elevated' if avg_congestion > 60 else 'Normal'
            },
            'arbitrage_implications': [
                'Favor land-bridge routes over all-water' if avg_congestion > 60 else 'Standard routing optimal',
                'Consider air freight for high-value/time-sensitive' if avg_congestion > 70 else None,
                'Build inventory buffers' if avg_congestion > 65 else 'JIT inventory viable'
            ]
        }


# Usage
def find_commodity_arbitrage(commodity: str, prices: Dict[str, float]) -> List[Dict]:
    """Quick geographic arbitrage search"""
    analyzer = DeepSupplyChainAnalyzer()
    return analyzer.find_geographic_arbitrage(commodity, prices)


def analyze_storage_trade(commodity: str, current: float, 
                         storage_monthly: float, forwards: Dict[str, float]) -> Dict:
    """Analyze temporal storage arbitrage"""
    analyzer = DeepSupplyChainAnalyzer()
    return analyzer.analyze_temporal_storage(commodity, current, storage_monthly, forwards)


def get_congestion_status() -> Dict:
    """Get port congestion report"""
    analyzer = DeepSupplyChainAnalyzer()
    return analyzer.get_port_congestion_report()
