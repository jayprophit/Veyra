"""
Vintage Car Investment Tracker
================================
Track classic and vintage car investments
Ferrari, Porsche, Mercedes, muscle cars
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CarEra(Enum):
    PRE_WAR = "pre_war"  # Before 1945
    POST_WAR = "post_war"  # 1945-1960
    CLASSIC = "classic"  # 1960-1980
    MODERN_CLASSIC = "modern_classic"  # 1980-2000
    CONTEMPORARY = "contemporary"  # 2000+


@dataclass
class VintageCar:
    make: str
    model: str
    year: int
    chassis_number: str
    condition: int  # 1-6 scale (1 = concours, 6 = parts car)
    mileage: int
    color: str
    engine: str
    transmission: str
    matching_numbers: bool
    provenance: List[str]
    
    # Financial
    purchase_price: float
    purchase_date: datetime
    current_estimate_low: float
    current_estimate_high: float
    restoration_costs: float


class VintageCarTracker:
    """Track vintage car investments"""
    
    # Hagerty Market Index components (approximate annual returns)
    CAR_INDICES = {
        'blue_chip': {'cagr_10yr': 0.089, 'description': 'Ferrari 250 GTO, Mercedes 300SL, etc.'},
        'affordable_classics': {'cagr_10yr': 0.045, 'description': 'Mass market classics'},
        'muscle_cars': {'cagr_10yr': 0.035, 'description': 'American muscle 1960s-70s'},
        'exotics': {'cagr_10yr': 0.075, 'description': 'Modern supercars as collectibles'},
        'porsche_911': {'cagr_10yr': 0.095, 'description': 'Air-cooled 911s (1964-1998)'}
    }
    
    # Top collectible cars by value
    BLUE_CHIP_CARS = {
        'Ferrari 250 GTO': {'record_sale': 70000000, 'production': 36},
        'Ferrari 250 Testa Rossa': {'record_sale': 16390000, 'production': 22},
        'Mercedes-Benz 300 SLR': {'record_sale': 142000000, 'production': 2},
        'Mercedes-Benz 300 SL Gullwing': {'record_sale': 6600000, 'production': 1400},
        'Porsche 917K': {'record_sale': 14000000, 'production': 12},
        'Ford GT40': {'record_sale': 11000000, 'production': 107},
        'Aston Martin DB4 GT Zagato': {'record_sale': 14500000, 'production': 19}
    }
    
    # Maintenance and storage costs (annual % of value)
    ANNUAL_COSTS = {
        'storage_premium': 0.015,  # 1.5%
        'insurance': 0.01,  # 1%
        'maintenance': 0.02,  # 2%
        'restoration_reserve': 0.01  # 1%
    }
    
    def analyze_car_performance(self, car: VintageCar) -> Dict:
        """Analyze vintage car investment performance"""
        
        current_mid = (car.current_estimate_low + car.current_estimate_high) / 2
        
        # Calculate returns
        holding_years = (datetime.now() - car.purchase_date).days / 365.25
        
        total_invested = car.purchase_price + car.restoration_costs
        
        if holding_years > 0:
            total_return = (current_mid - total_invested) / total_invested
            annualized = (1 + total_return) ** (1 / holding_years) - 1
        else:
            total_return = 0
            annualized = 0
        
        # Annual carrying costs
        annual_costs = current_mid * sum(self.ANNUAL_COSTS.values())
        
        # Net position
        net_gain = current_mid - total_invested - (annual_costs * holding_years)
        
        # Car era classification
        era = self._classify_era(car.year)
        
        # Condition impact
        condition_premium = self._condition_premium(car.condition)
        
        return {
            'car': f"{car.year} {car.make} {car.model}",
            'chassis': car.chassis_number[-6:] if len(car.chassis_number) > 6 else car.chassis_number,
            'era': era,
            'condition': self._condition_description(car.condition),
            'condition_score': car.condition,
            'matching_numbers': car.matching_numbers,
            'total_invested': round(total_invested, 0),
            'current_value': round(current_mid, 0),
            'unrealized_gain': round(current_mid - total_invested, 0),
            'annualized_return_pct': round(annualized * 100, 1),
            'annual_carrying_costs': round(annual_costs, 0),
            'holding_period_years': round(holding_years, 1),
            'condition_premium_factor': condition_premium,
            'rarity_score': self._calculate_rarity(car),
            'recommendation': self._car_recommendation(car, annualized, current_mid)
        }
    
    def _classify_era(self, year: int) -> str:
        """Classify car by era"""
        if year < 1945:
            return CarEra.PRE_WAR.value
        elif year < 1960:
            return CarEra.POST_WAR.value
        elif year < 1980:
            return CarEra.CLASSIC.value
        elif year < 2000:
            return CarEra.MODERN_CLASSIC.value
        else:
            return CarEra.CONTEMPORARY.value
    
    def _condition_description(self, condition: int) -> str:
        """Convert condition number to description"""
        descriptions = {
            1: 'Concours - Perfect, show winning',
            2: 'Excellent - Professionally restored',
            3: 'Good - Well maintained driver',
            4: 'Fair - Needs some work',
            5: 'Poor - Major restoration needed',
            6: 'Parts car - Not running'
        }
        return descriptions.get(condition, 'Unknown')
    
    def _condition_premium(self, condition: int) -> float:
        """Calculate condition impact on value"""
        premiums = {
            1: 2.5,  # Concours = 250% of #3 value
            2: 1.5,  # Excellent = 150%
            3: 1.0,  # Good = baseline
            4: 0.6,  # Fair = 60%
            5: 0.3,  # Poor = 30%
            6: 0.1   # Parts = 10%
        }
        return premiums.get(condition, 1.0)
    
    def _calculate_rarity(self, car: VintageCar) -> str:
        """Calculate rarity score"""
        car_key = f"{car.make} {car.model}"
        
        if car_key in self.BLUE_CHIP_CARS:
            production = self.BLUE_CHIP_CARS[car_key]['production']
            if production < 50:
                return 'ULTRA_RARE'
            elif production < 200:
                return 'VERY_RARE'
            else:
                return 'RARE'
        
        if not car.matching_numbers:
            return 'MODIFIED'
        
        if car.year < 1970:
            return 'VINTAGE'
        
        return 'STANDARD'
    
    def _car_recommendation(self, car: VintageCar, 
                           annualized_return: float,
                           current_value: float) -> str:
        """Generate car investment recommendation"""
        if annualized_return > 0.25:
            return "CONSIDER_SALE - Exceptional appreciation"
        elif annualized_return < -0.15:
            return "HOLD - Downside limited in rare cars"
        elif car.condition == 1 and current_value > 1000000:
            return "SHOW/SELL - Concours condition maximizes value"
        elif car.condition >= 4:
            return "RESTORE - Major value unlock via restoration"
        elif car.year < 1960 and car.matching_numbers:
            return "HOLD_LONG_TERM - Classic era, appreciating"
        else:
            return "ENJOY/HOLD - Use as intended, long term hold"
    
    def get_market_outlook(self) -> Dict:
        """Get vintage car market outlook"""
        return {
            'market_trend': 'SELECTIVE_APPRECIATION',
            'index_returns': {k: f"{v['cagr_10yr']*100:.1f}%" for k, v in self.CAR_INDICES.items()},
            'hot_segments': [
                'Air-cooled Porsches (911, 930)',
                'Manual transmission supercars',
                'Group B rally homologation cars',
                'Youngtimer Mercedes (1980s-90s)'
            ],
            'cooling_segments': [
                '1960s American muscle (oversupply)',
                '1960s Ferrari (too expensive)',
                'Pre-war classics (aging collector base)'
            ],
            'investment_characteristics': {
                'liquidity': 'LOW - 3-12 months to sell',
                'transaction_costs': '10% buyer premium + 5% seller',
                'storage': '$300-1000/month climate controlled',
                'maintenance': '$2000-10000/year',
                'insurance': '1-2% annually'
            },
            'key_auctions': ['Pebble Beach', 'Monterey', 'Amelia Island', 'Goodwood']
        }


# Usage
def analyze_vintage_car(make: str, model: str, year: int,
                        purchase: float, current_low: float, current_high: float,
                        condition: int = 3, matching: bool = True) -> Dict:
    """Quick car analysis"""
    tracker = VintageCarTracker()
    
    car = VintageCar(
        make=make,
        model=model,
        year=year,
        chassis_number='123456',
        condition=condition,
        mileage=50000,
        color='Rosso Corsa',
        engine='V12',
        transmission='Manual',
        matching_numbers=matching,
        provenance=['Original owner', 'Restored 2015'],
        purchase_price=purchase,
        purchase_date=datetime.now() - __import__('datetime').timedelta(days=365*3),
        current_estimate_low=current_low,
        current_estimate_high=current_high,
        restoration_costs=0
    )
    
    return tracker.analyze_car_performance(car)


def get_car_market_outlook() -> Dict:
    """Get car market outlook"""
    tracker = VintageCarTracker()
    return tracker.get_market_outlook()
