"""
Asteroid Mining Economics Model
================================
Detailed economic modeling for asteroid mining operations
Resource valuation, mission costs, ROI projections
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AsteroidTarget:
    name: str
    designation: str
    asteroid_type: str
    distance_au: float
    estimated_mass_tons: float
    resources: Dict[str, float]
    accessibility_score: float


class AsteroidMiningEconomics:
    """Economic modeling for asteroid mining ventures"""
    
    TARGET_ASTEROIDS = [
        AsteroidTarget('Ryugu', '162173', 'C-type', 1.2, 4.5e8,
                      {'water': 0.15, 'organics': 0.10, 'minerals': 0.75}, 0.7),
        AsteroidTarget('Bennu', '101955', 'B-type', 1.2, 7.8e7,
                      {'water': 0.12, 'carbon': 0.08, 'silicates': 0.80}, 0.6),
        AsteroidTarget('16 Psyche', '16', 'M-type', 2.9, 2.7e10,
                      {'iron': 0.90, 'nickel': 0.08, 'gold': 0.0001, 'platinum': 0.0005}, 0.4),
        AsteroidTarget('Didymos', '65803', 'S-type', 0.7, 5.2e8,
                      {'silicates': 0.85, 'nickel_iron': 0.15}, 0.8),
        AsteroidTarget('2016 HO3', '469219', 'S-type', 0.03, 4.1e6,
                      {'silicates': 0.80, 'metals': 0.20}, 0.95),
    ]
    
    # Space resource values (USD per ton in orbit)
    RESOURCE_VALUES = {
        'water': 50_000_000,
        'platinum_group': 50_000_000,
        'iron': 10_000,
        'nickel': 20_000,
        'rare_earths': 1_000_000,
        'gold': 60_000_000,
        'construction_aggregate': 5_000
    }
    
    # Mission cost components (USD)
    MISSION_COSTS = {
        'launch': 100_000_000,  # Falcon Heavy class
        'spacecraft': 250_000_000,
        'propulsion': 150_000_000,
        'mining_equipment': 200_000_000,
        'processing': 100_000_000,
        'operations_annual': 50_000_000,
        'return_transport': 75_000_000
    }
    
    def calculate_mission_economics(self, target: AsteroidTarget,
                                    extraction_rate_tons_per_year: float = 1000,
                                    mission_duration_years: int = 5) -> Dict:
        """Calculate mission economics for asteroid mining"""
        
        # Total mission cost
        total_cost = sum(self.MISSION_COSTS.values())
        total_cost += self.MISSION_COSTS['operations_annual'] * mission_duration_years
        
        # Calculate resource value
        annual_extraction = extraction_rate_tons_per_year
        total_extraction = annual_extraction * mission_duration_years
        
        # Value by resource type
        resource_values = {}
        total_value = 0
        
        for resource, percentage in target.resources.items():
            amount = total_extraction * percentage
            value_per_ton = self.RESOURCE_VALUES.get(resource, 0)
            value = amount * value_per_ton
            
            resource_values[resource] = {
                'amount_tons': round(amount, 1),
                'value_usd': round(value, 0),
                'percentage': percentage
            }
            total_value += value
        
        # ROI calculation
        roi = (total_value - total_cost) / total_cost if total_cost > 0 else 0
        
        # Break-even
        break_even_years = total_cost / (total_value / mission_duration_years) if total_value > 0 else float('inf')
        
        return {
            'target': target.name,
            'designation': target.designation,
            'mission_duration_years': mission_duration_years,
            'total_mission_cost': round(total_cost, 0),
            'total_resource_value': round(total_value, 0),
            'net_profit': round(total_value - total_cost, 0),
            'roi_pct': round(roi * 100, 1),
            'break_even_years': round(break_even_years, 1) if break_even_years != float('inf') else 'Never',
            'resource_breakdown': resource_values,
            'accessibility_score': target.accessibility_score,
            'viable': roi > 0.5 and break_even_years < 10,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_investment_thesis(self) -> Dict:
        """Get asteroid mining investment thesis"""
        return {
            'market_size_2040': '$100 billion',
            'key_drivers': [
                'Launch costs declining (SpaceX Starship)',
                'Water for propellant in orbit',
                'Platinum group metals for Earth use',
                'Construction materials for space infrastructure'
            ],
            'timeline': {
                '2025_2030': 'Demonstration missions, technology validation',
                '2030_2035': 'First commercial water extraction',
                '2035_2040': 'Platinum group metal return to Earth',
                '2040_plus': 'Full-scale industrial operations'
            },
            'public_companies': ['PL (Planet Labs)', 'RKLB (Rocket Lab)', 'ASTS (AST SpaceMobile)'],
            'private_companies': ['TransAstra', 'AstroForge', 'Karman+'],
            'risks': [
                'Technology unproven at scale',
                'Regulatory uncertainty',
                'Long time horizons',
                'High capital requirements'
            ]
        }


# Usage
def analyze_asteroid_mining(target_name: str = '16 Psyche') -> Dict:
    """Quick asteroid mining analysis"""
    economics = AsteroidMiningEconomics()
    
    target = next((t for t in economics.TARGET_ASTEROIDS if t.name == target_name), None)
    if not target:
        return {'error': f'Target {target_name} not found'}
    
    return economics.calculate_mission_economics(target)


def get_space_mining_outlook() -> Dict:
    """Get space mining investment outlook"""
    economics = AsteroidMiningEconomics()
    return economics.get_investment_thesis()
