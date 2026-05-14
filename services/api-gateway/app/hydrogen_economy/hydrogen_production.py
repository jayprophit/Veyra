"""Hydrogen Production Economics"""
from typing import Dict

class HydrogenProduction:
    """Green, blue, and grey hydrogen production economics"""
    
    def __init__(self, method: str = "electrolysis"):
        self.method = method  # electrolysis, steam_methane_reforming, coal_gasification
    
    def production_cost(self, electricity_price_mwh: float = 50) -> Dict:
        methods = {
            "grey": {
                "feedstock_cost": 1.50,  # $/kg H2
                "energy_cost": 0.50,
                "capex_recovery": 0.30,
                "opex": 0.20,
                "carbon_cost": 0.0,
                "total": 2.50
            },
            "blue": {
                "feedstock_cost": 1.50,
                "energy_cost": 0.50,
                "capex_recovery": 0.50,
                "opex": 0.30,
                "carbon_capture_cost": 0.80,
                "total": 3.60
            },
            "green": {
                "electricity_kwh_per_kg": 50,  # kWh/kg H2
                "electricity_cost": (50 * electricity_price_mwh) / 1000,
                "electrolyzer_capex_recovery": 1.50,
                "opex": 0.50,
                "total": None  # Calculated below
            }
        }
        
        if self.method == "green":
            green_data = methods["green"]
            total = green_data["electricity_cost"] + green_data["electrolyzer_capex_recovery"] + green_data["opex"]
            green_data["total"] = total
            return green_data
        
        return methods.get(self.method, methods["green"])
    
    def electrolyzer_economics(self, capacity_mw: float = 100) -> Dict:
        # PEM electrolyzer costs
        capex_per_mw = 800000  # $800/kW
        total_capex = capacity_mw * capex_per_mw
        
        # Production
        utilization = 0.50  # 50% capacity factor (renewable)
        annual_hours = 8760 * utilization
        kwh_per_kg = 50
        
        annual_production_tons = (capacity_mw * 1000 * annual_hours) / kwh_per_kg / 1000
        
        return {
            "capex_millions": total_capex / 1e6,
            "capacity_mw": capacity_mw,
            "annual_production_tons": round(annual_production_tons, 0),
            "capex_per_ton_annual": round(total_capex / annual_production_tons, 0),
            "utilization": utilization,
            "technology": "PEM Electrolysis"
        }
    
    def transport_cost(self, distance_km: float = 500, method: str = "pipeline") -> Dict:
        costs = {
            "pipeline": 0.10 * distance_km,  # $/kg for 500km
            "tube_trailer": 2.00 + (0.005 * distance_km),
            "liquid": 1.50 + (0.003 * distance_km),
            "ammonia": 1.00 + (0.002 * distance_km)
        }
        
        return {
            "transport_method": method,
            "distance_km": distance_km,
            "cost_per_kg": round(costs.get(method, costs["pipeline"]), 2),
            "break_even_distance": "Pipeline favored >200km at scale"
        }
    
    def end_use_economics(self, application: str = "refining") -> Dict:
        uses = {
            "refining": {"willingness_to_pay": 2.50, "volume_ktpa": 40000},
            "ammonia": {"willingness_to_pay": 3.00, "volume_ktpa": 30000},
            "steel": {"willingness_to_pay": 4.00, "volume_ktpa": 5000},
            "mobility": {"willingness_to_pay": 6.00, "volume_ktpa": 1000},
            "power": {"willingness_to_pay": 5.00, "volume_ktpa": 2000}
        }
        
        data = uses.get(application, uses["refining"])
        grey_cost = 2.50
        
        return {
            "application": application,
            "willingness_to_pay": data["willingness_to_pay"],
            "grey_hydrogen_cost": grey_cost,
            "green_premium": data["willingness_to_pay"] - grey_cost,
            "market_size_ktpa": data["volume_ktpa"],
            "green_competitive": data["willingness_to_pay"] > 4.00
        }
