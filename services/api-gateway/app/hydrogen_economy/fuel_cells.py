"""Fuel Cell Economics"""
from typing import Dict

class FuelCellEconomics:
    """PEM and SOFC fuel cell system economics"""
    
    def __init__(self, fuel_cell_type: str = "pem"):
        self.fc_type = fuel_cell_type  # pem, sofc, pafc
    
    def system_cost(self, power_kw: float = 100) -> Dict:
        costs_per_kw = {
            "pem": 1500,  # $/kW
            "sofc": 8000,
            "pafc": 6000
        }
        
        cost_per_kw = costs_per_kw.get(self.fc_type, 1500)
        system_cost = power_kw * cost_per_kw
        
        # Learning curve projection
        learning_rate = 0.15  # 15% cost reduction per doubling
        doublings = 5
        future_cost = system_cost * ((1 - learning_rate) ** doublings)
        
        return {
            "current_cost_per_kw": cost_per_kw,
            "system_cost": system_cost,
            "power_kw": power_kw,
            "future_cost_2030": round(future_cost, 0),
            "target_2030_doe": 150 * power_kw,  # $150/kW target
            "gap_to_target": round((system_cost - 150 * power_kw) / (150 * power_kw), 1)
        }
    
    def operating_cost(self, annual_hours: float = 8000) -> Dict:
        # Maintenance and fuel
        maintenance_per_kwh = 0.03
        hydrogen_consumption_kwh = 1.30  # kg H2 per kWh electrical
        hydrogen_price = 5.00  # $/kg
        
        fuel_cost = hydrogen_consumption_kwh * hydrogen_price
        maintenance = maintenance_per_kwh
        
        total_lcoe = fuel_cost + maintenance
        
        return {
            "fuel_cost_per_kwh": fuel_cost,
            "maintenance_per_kwh": maintenance,
            "total_lcoe": round(total_lcoe, 3),
            "efficiency_pct": 50,  # HHV
            "vs_diesel_generator": "2-3x more expensive"
        }
    
    def automotive_application(self, vehicle_range_km: float = 500) -> Dict:
        # FCEV economics
        storage_kg = 5  # kg H2 for 500km
        tank_cost = 3000
        fuel_cell_system = 15000  # 100kW @ $150/kW
        
        powertrain_cost = tank_cost + fuel_cell_system
        
        # Compare to BEV
        bev_battery_cost = 15000  # 75kWh @ $200/kWh
        
        return {
            "fcev_powertrain_cost": powertrain_cost,
            "bev_powertrain_cost": bev_battery_cost,
            "premium_vs_bev": powertrain_cost - bev_battery_cost,
            "refuel_time_minutes": 5,
            "vs_bev_charge": "30-50x faster",
            "hydrogen_cost_per_100km": 6.00,
            "electricity_cost_per_100km": 3.00
        }
    
    def stationary_power(self, application: str = "backup") -> Dict:
        applications = {
            "backup": {
                "value_proposition": "Reliability",
                "competition": "Diesel generators",
                "payback_years": 10,
                "market": "Data centers, hospitals"
            },
            "chp": {
                "value_proposition": "Efficiency + heat",
                "competition": "Grid + boiler",
                "payback_years": 7,
                "market": "Industrial facilities"
            },
            "prime_power": {
                "value_proposition": "Zero emissions",
                "competition": "Grid",
                "payback_years": 15,
                "market": "Remote/off-grid"
            }
        }
        
        return applications.get(application, applications["backup"])
