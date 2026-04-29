"""Space Defense - Military space and satellite defense"""
from typing import Dict

class SpaceDefense:
    """Analyze space defense investments"""
    
    def satellite_protection_value(self, satellite_cost: float,
                                  mission_criticality: str,
                                  threat_level: str) -> Dict:
        """Value satellite protection systems"""
        # Protection as % of satellite cost
        base_protection_pct = 0.15
        
        criticality_mult = {"high": 2.0, "medium": 1.0, "low": 0.5}
        threat_mult = {"high": 2.0, "medium": 1.2, "low": 0.8}
        
        protection_value = (satellite_cost * base_protection_pct * 
                          criticality_mult.get(mission_criticality, 1) * 
                          threat_mult.get(threat_level, 1))
        
        return {
            "satellite_cost": satellite_cost,
            "protection_value": round(protection_value, 0),
            "protection_as_pct": round(protection_value / satellite_cost * 100, 1),
            "justified": protection_value < satellite_cost * 0.5
        }
    
    def constellation_economics(self, sat_count: int,
                              sat_cost: float,
                              launch_cost_per_sat: float,
                              annual_revenue_per_sat: float) -> Dict:
        """Analyze satellite constellation economics"""
        total_deployment = sat_count * (sat_cost + launch_cost_per_sat)
        annual_revenue = sat_count * annual_revenue_per_sat
        
        # Constellation premium (network effect)
        network_premium = 1 + min(sat_count / 100, 1.0)  # Up to 2x
        adjusted_revenue = annual_revenue * network_premium
        
        payback = total_deployment / adjusted_revenue if adjusted_revenue > 0 else 999
        
        return {
            "constellation_size": sat_count,
            "deployment_cost": total_deployment,
            "annual_revenue": round(adjusted_revenue, 0),
            "payback_years": round(payback, 1),
            "network_premium": round(network_premium, 2),
            "economically_viable": payback < 7
        }
