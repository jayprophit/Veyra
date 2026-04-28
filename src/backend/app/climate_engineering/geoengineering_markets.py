"""Geoengineering Markets - Solar radiation management economics"""
from typing import Dict

class GeoengineeringMarkets:
    """Markets for geoengineering services"""
    
    def stratospheric_aerosol_cost(self, tons_so2_per_year: float,
                                  aircraft_cost_per_hour: float,
                                  flights_per_year: int) -> Dict:
        """Cost of stratospheric aerosol injection program"""
        material_cost = tons_so2_per_year * 500  # $500/ton SO2
        flight_hours = flights_per_year * 10
        aircraft_cost = flight_hours * aircraft_cost_per_hour
        
        total_annual = material_cost + aircraft_cost
        
        return {
            "material_cost": round(material_cost, 0),
            "aircraft_operating_cost": round(aircraft_cost, 0),
            "total_annual_cost": round(total_annual, 0),
            "cost_per_deg_cooling": round(total_annual / 0.1, 0),  # Assuming 0.1C cooling
            "program_duration_years": 50
        }
    
    def cloud_brightening_economics(self, vessels: int,
                                   spray_rate_per_vessel: float,
                                   operating_days: int) -> Dict:
        """Marine cloud brightening fleet economics"""
        vessel_cost_per_day = 50000
        total_vessel_cost = vessels * vessel_cost_per_day * operating_days
        
        equipment_capex = vessels * 2000000  # $2M per vessel
        
        annual_cost = total_vessel_cost + (equipment_capex / 10)  # 10-year depreciation
        
        # Estimated cooling effect
        cooling_watts_per_m2 = 2
        area_covered = vessels * spray_rate_per_vessel * operating_days * 1000  # km2
        
        return {
            "fleet_size": vessels,
            "annual_operating_cost": round(total_vessel_cost, 0),
            "equipment_capex": equipment_capex,
            "total_annual_cost": round(annual_cost, 0),
            "area_covered_km2": round(area_covered, 0),
            "cost_per_km2": round(annual_cost / area_covered, 2) if area_covered > 0 else 0
        }
    
    def space_sunshade_cost(self, shade_area_km2: float,
                           launch_cost_per_kg: float,
                           shade_mass_per_km2: float) -> Dict:
        """Cost of Lagrange point sunshade"""
        total_mass = shade_area_km2 * shade_mass_per_km2
        launch_cost = total_mass * launch_cost_per_kg
        manufacturing_cost = shade_area_km2 * 1000000  # $1M per km2
        
        total_cost = launch_cost + manufacturing_cost
        
        return {
            "shade_area_km2": shade_area_km2,
            "total_mass_tons": round(total_mass / 1000, 0),
            "launch_cost": round(launch_cost, 0),
            "manufacturing_cost": round(manufacturing_cost, 0),
            "total_mission_cost": round(total_cost, 0),
            "cooling_effect_celsius": 0.5,  # Estimate
            "cost_per_0_1c_cooling": round(total_cost / 5, 0)
        }
