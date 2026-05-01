"""eVTOL Operations"""
from typing import Dict

class EVTOLOperations:
    """Urban air mobility economics"""
    
    def aircraft_comparison(self) -> Dict:
        return {
            "joby": {
                "range_km": 240,
                "passengers": 4,
                "noise_db": 65,
                "certification": "2025 target",
                "funding": 2e9
            },
            "archer": {
                "range_km": 97,
                "passengers": 4,
                "partner": "United Airlines",
                "orders": 1000,
                "valuation": 1.5e9
            },
            "lilium": {
                "range_km": 250,
                "passengers": 6,
                "approach": "Jet engines",
                "location": "Germany"
            },
            "vertical_aerospace": {
                "partner": "American Airlines",
                "aircraft": "VA-X4",
                "orders": 1000
            }
        }
    
    def operating_costs(self) -> Dict:
        return {
            "energy_per_mile": 0.10,
            "maintenance_per_hour": 150,
            "pilot_cost_per_hour": 75,
            "insurance_per_hour": 50,
            "total_per_hour_manned": 275,
            "total_per_hour_autonomous": 200
        }
    
    def unit_economics(self) -> Dict:
        # 25 mile trip
        revenue = 100  # $100 fare
        cost_manned = 275 * (25 / 150)  # 150 mph cruise
        cost_auto = 200 * (25 / 150)
        
        return {
            "trip_revenue": revenue,
            "cost_manned": round(cost_manned, 2),
            "margin_manned_pct": round((revenue - cost_manned) / revenue * 100, 1),
            "cost_autonomous": round(cost_auto, 2),
            "margin_autonomous_pct": round((revenue - cost_auto) / revenue * 100, 1)
        }
