"""
Wine & Spirits Investment Tracker
==================================
Track fine wine and spirits investments
Bordeaux, Burgundy, Scotch whisky, rare spirits
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class WineRegion(Enum):
    BORDEAUX = "bordeaux"
    BURGUNDY = "burgundy"
    CHAMPAGNE = "champagne"
    TUSCANY = "tuscany"
    NAPA = "napa"
    RIOJA = "rioja"


@dataclass
class WineHolding:
    producer: str
    wine_name: str
    vintage: int
    region: str
    format: str  # 'bottle', 'magnum', 'case'
    quantity: int
    purchase_price_per_unit: float
    current_price_estimate: float
    purchase_date: datetime
    storage_location: str
    drinking_window: str


class WineInvestmentTracker:
    """Track fine wine and spirits investments"""
    
    # Wine market indices (Liv-ex 1000 components)
    WINE_INDICES = {
        'liv_ex_1000': {'cagr_10yr': 0.055, 'volatility': 0.08},
        'liv_ex_bordeaux_500': {'cagr_10yr': 0.045, 'volatility': 0.07},
        'liv_ex_burgundy_150': {'cagr_10yr': 0.095, 'volatility': 0.15},
        'liv_ex_champagne_50': {'cagr_10yr': 0.075, 'volatility': 0.10},
        'liv_ex_italy_100': {'cagr_10yr': 0.065, 'volatility': 0.09},
        'rare_whisky_apex_1000': {'cagr_10yr': 0.12, 'volatility': 0.20}
    }
    
    # Top investment grade wines
    BLUE_CHIP_WINES = {
        'bordeaux': [
            'Chateau Margaux', 'Chateau Latour', 'Chateau Lafite',
            'Chateau Mouton Rothschild', 'Chateau Haut-Brion',
            'Petrus', 'Cheval Blanc'
        ],
        'burgundy': [
            'Domaine de la Romanee-Conti', 'Domaine Leroy',
            'Domaine Armand Rousseau', 'Domaine Leflaive',
            'Henri Jayer', 'Georges Roumier'
        ],
        'champagne': [
            'Krug Clos du Mesnil', 'Salon',
            'Dom Perignon P2/P3', 'Krug Vintage'
        ],
        'whisky': [
            'Macallan Fine & Rare', 'Yamazaki Sherry Cask',
            'Karuizawa', 'Springbank'
        ]
    }
    
    # Storage costs
    STORAGE_COSTS = {
        'professional_warehouse': 0.015,  # 1.5% annually
        'bonded_warehouse': 0.010,  # 1% annually (tax advantage)
        'private_cellar': 0.005  # 0.5% (assuming owned space)
    }
    
    def analyze_wine_performance(self, holding: WineHolding) -> Dict:
        """Analyze wine investment performance"""
        
        # Current value
        current_total = holding.current_price_estimate * holding.quantity
        purchase_total = holding.purchase_price_per_unit * holding.quantity
        
        # Calculate returns
        holding_days = (datetime.now() - holding.purchase_date).days
        holding_years = holding_days / 365.25
        
        if holding_years > 0:
            total_return = (current_total - purchase_total) / purchase_total
            annualized = (1 + total_return) ** (1 / holding_years) - 1
        else:
            total_return = 0
            annualized = 0
        
        # Storage costs
        storage_rate = self.STORAGE_COSTS.get('professional_warehouse', 0.015)
        storage_cost = purchase_total * storage_rate * holding_years
        
        # Net return
        net_return = (current_total - purchase_total - storage_cost) / purchase_total
        
        # Drinking window assessment
        current_year = datetime.now().year
        drinking_status = self._assess_drinking_window(holding.drinking_window, current_year)
        
        return {
            'wine': f"{holding.producer} {holding.wine_name} {holding.vintage}",
            'region': holding.region,
            'format': holding.format,
            'quantity': holding.quantity,
            'purchase_total': round(purchase_total, 0),
            'current_value': round(current_total, 0),
            'gross_unrealized_gain': round(current_total - purchase_total, 0),
            'storage_costs': round(storage_cost, 0),
            'net_unrealized_gain': round(current_total - purchase_total - storage_cost, 0),
            'holding_period_years': round(holding_years, 1),
            'gross_annualized_return_pct': round(annualized * 100, 1),
            'net_annualized_return_pct': round(((1 + net_return) ** (1 / holding_years) - 1) * 100, 1) if holding_years > 0 else 0,
            'drinking_window_status': drinking_status,
            'recommendation': self._wine_recommendation(holding, annualized, drinking_status)
        }
    
    def _assess_drinking_window(self, window: str, current_year: int) -> str:
        """Assess drinking window status"""
        # Parse window like "2025-2040"
        try:
            years = window.split('-')
            if len(years) == 2:
                start = int(years[0].strip())
                end = int(years[1].strip())
                
                if current_year < start:
                    return f"TOO_YOUNG - Wait {start - current_year} years"
                elif current_year > end:
                    return "PAST_PRIME - Drink immediately or sell"
                elif current_year > end - 5:
                    return "APPROACHING_PEAK - Optimal drinking now"
                else:
                    return f"DEVELOPING - Peak in {start + (end - start) // 2 - current_year} years"
            else:
                return "UNKNOWN"
        except:
            return "UNKNOWN"
    
    def _wine_recommendation(self, holding: WineHolding, 
                             annualized_return: float,
                             drinking_status: str) -> str:
        """Generate wine investment recommendation"""
        if "PAST_PRIME" in drinking_status:
            return "URGENT_SELL - Past drinking window, value declining"
        elif annualized_return > 0.15 and "APPROACHING_PEAK" in drinking_status:
            return "SELL - High appreciation + approaching peak"
        elif annualized_return > 0.20:
            return "CONSIDER_PROFIT_TAKING - Exceptional gains"
        elif annualized_return < -0.10:
            return "HOLD - Downside limited, wine cyclical"
        elif "TOO_YOUNG" in drinking_status:
            return "HOLD_LONG_TERM - Appreciation potential high"
        else:
            return "HOLD - Continue monitoring"
    
    def get_region_outlook(self, region: str) -> Dict:
        """Get investment outlook by region"""
        
        outlooks = {
            'bordeaux': {
                'trend': 'STABLE',
                'cagr_10yr': '4.5%',
                'characteristics': 'Liquid, established, lower volatility',
                'recommendation': 'CORE_HOLDING - Portfolio anchor'
            },
            'burgundy': {
                'trend': 'STRONG_BUT_VOLATILE',
                'cagr_10yr': '9.5%',
                'characteristics': 'Supply constrained, high demand, scarcity premium',
                'recommendation': 'GROWTH_ALLOCATION - 20-30% of portfolio'
            },
            'champagne': {
                'trend': 'STRONG',
                'cagr_10yr': '7.5%',
                'characteristics': 'Improving quality perception, vintage prestige',
                'recommendation': 'OPPORTUNITY - Building momentum'
            },
            'rare_whisky': {
                'trend': 'VERY_STRONG_BUT_RISKY',
                'cagr_10yr': '12%',
                'characteristics': 'High volatility, speculative, fashion dependent',
                'recommendation': 'SATELLITE_ALLOCATION - 5-10% max'
            }
        }
        
        return outlooks.get(region.lower(), {'error': f'No outlook for {region}'})
    
    def get_portfolio_allocation(self, total_value: float) -> Dict:
        """Get recommended wine portfolio allocation"""
        
        if total_value < 10000:
            rec_allocation = {
                'bordeaux': 0.50,
                'burgundy': 0.20,
                'champagne': 0.20,
                'other': 0.10
            }
            strategy = 'Focus on liquid, blue-chip wines'
        elif total_value < 50000:
            rec_allocation = {
                'bordeaux': 0.40,
                'burgundy': 0.30,
                'champagne': 0.15,
                'rhone': 0.10,
                'italy': 0.05
            }
            strategy = 'Diversified with growth tilt'
        else:
            rec_allocation = {
                'bordeaux': 0.35,
                'burgundy': 0.30,
                'champagne': 0.15,
                'rhone': 0.10,
                'italy': 0.05,
                'rare_whisky': 0.05
            }
            strategy = 'Full diversification with alternative spirits'
        
        return {
            'total_portfolio_value': round(total_value, 0),
            'recommended_allocation': {
                region: {
                    'pct': pct * 100,
                    'value': round(total_value * pct, 0)
                }
                for region, pct in rec_allocation.items()
            },
            'strategy': strategy,
            'expected_return': f"{self.WINE_INDICES['liv_ex_1000']['cagr_10yr']*100:.1f}% annually",
            'storage_annual_cost': round(total_value * 0.015, 0),
            'insurance_annual_cost': round(total_value * 0.005, 0)
        }


# Usage
def analyze_wine(producer: str, name: str, vintage: int,
                region: str, purchase: float, current: float,
                qty: int = 1) -> Dict:
    """Quick wine analysis"""
    tracker = WineInvestmentTracker()
    
    holding = WineHolding(
        producer=producer,
        wine_name=name,
        vintage=vintage,
        region=region,
        format='bottle',
        quantity=qty,
        purchase_price_per_unit=purchase,
        current_price_estimate=current,
        purchase_date=datetime.now() - __import__('datetime').timedelta(days=365*2),
        storage_location='Professional Warehouse',
        drinking_window=f'{vintage+10}-{vintage+30}'
    )
    
    return tracker.analyze_wine_performance(holding)


def get_wine_outlook(region: str) -> Dict:
    """Get wine region outlook"""
    tracker = WineInvestmentTracker()
    return tracker.get_region_outlook(region)


def get_wine_allocation(portfolio: float) -> Dict:
    """Get wine portfolio allocation"""
    tracker = WineInvestmentTracker()
    return tracker.get_portfolio_allocation(portfolio)
