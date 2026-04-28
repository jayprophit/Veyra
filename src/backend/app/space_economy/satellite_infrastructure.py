"""Satellite Infrastructure - Analysis of satellite economy"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Satellite:
    name: str
    operator: str
    orbit_type: str
    launch_cost: float
    revenue_per_year: float
    lifespan: int

class SatelliteInfrastructure:
    """Analyze satellite infrastructure investments"""
    
    ORBIT_TYPES = ["LEO", "MEO", "GEO"]
    
    def __init__(self):
        self.satellites: List[Satellite] = []
    
    def add_satellite(self, sat: Satellite):
        self.satellites.append(sat)
    
    def constellation_analysis(self, count: int, orbit: str) -> Dict:
        """Analyze satellite constellation economics"""
        launch_cost_per_sat = 50e6 if orbit == "LEO" else 100e6 if orbit == "MEO" else 200e6
        total_launch = launch_cost_per_sat * count
        
        ground_stations = count * 5e6
        operations = count * 2e6 * 5  # 5 years
        
        total_capex = total_launch + ground_stations + operations
        
        # Revenue potential
        coverage_area = count * (500 if orbit == "LEO" else 2000 if orbit == "MEO" else 8000)
        subscribers = coverage_area * 1000  # 1000 per sq km
        revenue_per_sub = 50  # monthly
        annual_revenue = subscribers * revenue_per_sub * 12
        
        return {
            "constellation_size": count,
            "orbit": orbit,
            "total_capex": total_capex,
            "annual_revenue": annual_revenue,
            "payback_years": round(total_capex / annual_revenue, 1),
            "coverage_sq_km": coverage_area,
            "potential_subscribers": subscribers
        }
    
    def starlink_competitor_analysis(self, capex: float) -> Dict:
        """Compare to Starlink economics"""
        starlink_capex = 10e9
        starlink_subs = 2e6
        
        market_share = capex / starlink_capex
        potential_subs = starlink_subs * market_share * 0.5  # Conservative
        
        return {
            "relative_to_starlink": market_share,
            "estimated_subscribers": potential_subs,
            "competitive_position": "LEADER" if market_share > 0.5 else "CHALLENGER" if market_share > 0.2 else "NICHE"
        }
