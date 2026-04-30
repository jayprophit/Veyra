"""Satellite Constellation Economics"""
from typing import Dict

class ConstellationEconomics:
    """LEO constellation business models"""
    
    def starlink_economics(self) -> Dict:
        return {
            "satellites_deployed": 5500,
            "target_constellation": 12000,
            "launch_cost_per_satellite": 0.5e6,
            "satellite_manufacturing_cost": 0.25e6,
            "total_capex_estimate": 30e9,
            "subscribers": 2.2e6,
            "revenue_annual": 3e9,
            "breakeven_subscribers": 10e6
        }
    
    def competitor_analysis(self) -> Dict:
        return {
            "oneweb": {"satellites": 634, "status": "Operational", "backers": "Eutelsat, UK gov"},
            "amazon_kuiper": {"satellites_planned": 3236, "launch": "2024", "investment": 10e9},
            "telesat_lightspeed": {"satellites": 198, "focus": "Enterprise", "funding": "4B CAD"}
        }
    
    def service_pricing(self) -> Dict:
        return {
            "starlink": {"hardware": 599, "monthly": 120, "business": 5000},
            "oneweb": {"monthly": 300, "enterprise_focus": True},
            "vs_fiber": {"rural_premium": 3.0, "value_prop": "Anywhere connectivity"}
        }
