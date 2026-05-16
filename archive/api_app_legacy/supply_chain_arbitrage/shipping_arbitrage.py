"""Shipping Arbitrage - Freight rates, vessel chartering, container trading"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class VesselType(Enum):
    BULK_CARRIER = "bulk_carrier"; TANKER = "tanker"
    CONTAINER = "container"; LNG_CARRIER = "lng_carrier"
    RORO = "roro"; CRUISE = "cruise"

class RouteType(Enum):
    DRY_BULK = "dry_bulk"; WET_BULK = "wet_bulk"
    CONTAINER = "container"; GAS = "gas"

@dataclass
class FreightContract:
    contract_id: str; vessel_type: VesselType
    route: str; cargo_type: str
    quantity_mt: Decimal; freight_rate_usd_day: Decimal
    duration_days: int; total_cost: Decimal = Decimal("0")

class ShippingArbitrage:
    """Global shipping and freight arbitrage"""
    
    def __init__(self):
        self.active_charters: Dict[str, FreightContract] = {}
        self.freight_indices = self._init_freight_indices()
        
    def _init_freight_indices(self):
        return {
            "BDI": {"name": "Baltic Dry Index", "value": 1650, "change_pct": 2.3},
            "BDTI": {"name": "Baltic Dirty Tanker", "value": 1120, "change_pct": -0.5},
            "BCTI": {"name": "Baltic Clean Tanker", "value": 890, "change_pct": 1.2},
            "BCI": {"name": "Capesize Index", "value": 2450, "change_pct": 3.1},
            "BPI": {"name": "Panamax Index", "value": 1380, "change_pct": 0.8},
            "BSI": {"name": "Supramax Index", "value": 1050, "change_pct": -1.2}
        }
    
    def get_freight_rates(self) -> Dict:
        """Get current freight rates by vessel type"""
        return {
            "capesize": {"rate_usd_day": 35000, "route": "Brazil-China", "cargo": "iron_ore"},
            "vlcc": {"rate_usd_day": 65000, "route": "Middle_East-Asia", "cargo": "crude_oil"},
            "aframax": {"rate_usd_day": 45000, "route": "North_Sea-Europe", "cargo": "crude_oil"},
            "panamax": {"rate_usd_day": 18000, "route": "US_Gulf-Asia", "cargo": "grains"},
            "supramax": {"rate_usd_day": 15000, "route": "SE_Asia-India", "cargo": "coal"},
            "lng_carrier": {"rate_usd_day": 120000, "route": "Qatar-Japan", "cargo": "LNG"},
            "container_8k": {"rate_usd_day": 25000, "route": "Asia-Europe", "cargo": "containers"}
        }
    
    def find_arbitrage(self) -> List[Dict]:
        """Find shipping rate arbitrage opportunities"""
        rates = self.get_freight_rates()
        opportunities = []
        
        # Spot vs Time charter spread
        for vessel, rate_data in rates.items():
            spot_rate = rate_data["rate_usd_day"]
            
            # Time charter rate (typically 20% discount to spot)
            time_charter_rate = spot_rate * 0.8
            
            # If spot is higher than time charter + operating costs
            daily_op_cost = 5000 if "container" in vessel else 8000  # Fuel + crew + maintenance
            
            if spot_rate > (time_charter_rate + daily_op_cost):
                spread = spot_rate - time_charter_rate - daily_op_cost
                opportunities.append({
                    "strategy": "spot_charter_spread",
                    "vessel_type": vessel,
                    "spot_rate": spot_rate,
                    "time_charter_rate": time_charter_rate,
                    "operating_cost": daily_op_cost,
                    "daily_spread": spread,
                    "annual_spread": spread * 365,
                    "route": rate_data["route"]
                })
        
        # Route arbitrage
        route_pairs = [
            ("Brazil-China", "Australia-China", "iron_ore"),
            ("Middle_East-Asia", "US_Gulf-Asia", "crude_oil"),
            ("US_Gulf-Europe", "Russia-Europe", "grains")
        ]
        
        return sorted(opportunities, key=lambda x: x["annual_spread"], reverse=True)
    
    def charter_vessel(self, vessel_type: str, route: str, 
                      days: int, strategy: str = "time_charter") -> Dict:
        """Charter a vessel for arbitrage"""
        rates = self.get_freight_rates()
        
        if vessel_type not in rates:
            return {"success": False, "error": "Unknown vessel type"}
        
        rate_data = rates[vessel_type]
        
        if strategy == "time_charter":
            daily_rate = rate_data["rate_usd_day"] * 0.8
        else:  # spot
            daily_rate = rate_data["rate_usd_day"]
        
        operating_cost = 6000  # Daily operating cost
        total_cost = (daily_rate + operating_cost) * days
        
        contract_id = f"SHIP_{date.today().isoformat()}_{vessel_type}"
        
        return {
            "success": True, "contract_id": contract_id,
            "vessel_type": vessel_type, "route": route,
            "charter_type": strategy, "daily_rate": daily_rate,
            "operating_cost": operating_cost, "duration_days": days,
            "total_cost": float(total_cost),
            "projected_revenue": float(daily_rate * days * Decimal("1.2")),
            "projected_profit": float(daily_rate * days * Decimal("0.2"))
        }
    
    def get_container_trading_opportunities(self) -> List[Dict]:
        """Trade shipping containers as assets"""
        return [
            {
                "type": "buy_containers",
                "container_type": "40ft_high_cube",
                "quantity": 100,
                "price_per_unit": 3500,
                "location": "Shanghai",
                "lease_rate_monthly": 85,
                "occupancy_rate_pct": 92,
                "annual_yield_pct": 29,
                "notes": "Container shortage arbitrage"
            },
            {
                "type": "sell_containers",
                "container_type": "40ft_standard",
                "quantity": 50,
                "price_per_unit": 4200,
                "location": "Rotterdam",
                "purchase_cost": 2800,
                "profit_per_unit": 1400,
                "total_profit": 70000,
                "notes": "Sell into high-demand European market"
            }
        ]
