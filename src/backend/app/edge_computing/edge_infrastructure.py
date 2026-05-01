"""Edge Infrastructure"""
from typing import Dict

class EdgeInfrastructure:
    """Edge data center and compute"""
    
    def infrastructure_types(self) -> Dict:
        return {
            "micro_data_centers": {
                "size": "10-100kW",
                "location": "Cell towers, buildings",
                "capex_per_kw": 8000
            },
            "regional_edge": {
                "size": "1-10MW",
                "latency": "10-20ms",
                "capex_per_mw": 6e6
            },
            "far_edge": {
                "size": "1-10kW",
                "location": "Factory floor, retail",
                "capex_per_kw": 12000
            }
        }
    
    def major_providers(self) -> Dict:
        return {
            "equinix": {"locations": 240, "edge_focus": True, "revenue_annual": 8e9},
            "fastly": {"pop_count": 95, "focus": "CDN + compute", "market_cap": 2e9},
            "cloudflare": {"data_centers": 300, "workers_platform": True, "revenue": 1.3e9},
            "vapor_io": {"focus": "Kinetic Edge", "funding": 90e6, "tower_strategy": True}
        }
    
    def latency_comparison(self) -> Dict:
        return {
            "cloud": {"latency_ms": 50, "use_case": "Batch processing"},
            "regional_edge": {"latency_ms": 15, "use_case": "Gaming, video"},
            "far_edge": {"latency_ms": 5, "use_case": "Autonomous, industrial"},
            "device": {"latency_ms": 0, "limitation": "Compute constrained"}
        }
