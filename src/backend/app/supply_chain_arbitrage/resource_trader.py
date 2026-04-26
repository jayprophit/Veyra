"""Resource Arbitrage Trader - Profit from supply/demand imbalances"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class ResourceType(Enum):
    CRUDE_OIL = "crude_oil"; NATURAL_GAS = "natural_gas"
    COPPER = "copper"; LITHIUM = "lithium"; COAL = "coal"
    WHEAT = "wheat"; COFFEE = "coffee"; GOLD = "gold"
    URANIUM = "uranium"; CARBON_CREDITS = "carbon_credits"

@dataclass
class ResourceContract:
    contract_id: str; resource_type: ResourceType
    quantity: Decimal; contract_price: Decimal
    source_location: str; destination_location: str
    delivery_date: date; transport_cost: Decimal
    net_profit: Decimal = Decimal("0")

class ResourceTrader:
    """Global Resource Arbitrage Platform"""
    
    def __init__(self):
        self.active_contracts: Dict[str, ResourceContract] = {}
        self.supply_chains = self._init_supply_chains()
        self.total_profit = Decimal("0")
    
    def _init_supply_chains(self):
        return {
            "us_asia_oil": {
                "resource": ResourceType.CRUDE_OIL,
                "source": "Texas, USA", "destination": "Singapore",
                "transport": "supertanker", "transit_days": 45,
                "cost_per_barrel": Decimal("2.50"),
                "typical_spread": Decimal("3.00")
            },
            "qatar_europe_lng": {
                "resource": ResourceType.NATURAL_GAS,
                "source": "Qatar", "destination": "Rotterdam",
                "transport": "LNG_carrier", "transit_days": 21,
                "cost_per_mmbtu": Decimal("1.20"),
                "typical_spread": Decimal("2.50")
            },
            "chile_china_copper": {
                "resource": ResourceType.COPPER,
                "source": "Chile", "destination": "Shanghai",
                "transport": "bulk_carrier", "transit_days": 35,
                "cost_per_tonne": Decimal("85"),
                "typical_spread": Decimal("150")
            },
            "australia_china_lithium": {
                "resource": ResourceType.LITHIUM,
                "source": "Australia", "destination": "China",
                "transport": "bulk_ship", "transit_days": 14,
                "cost_per_tonne": Decimal("120"),
                "typical_spread": Decimal("500")
            },
            "ukraine_mideast_wheat": {
                "resource": ResourceType.WHEAT,
                "source": "Ukraine", "destination": "Middle East",
                "transport": "grain_vessel", "transit_days": 7,
                "cost_per_tonne": Decimal("15"),
                "typical_spread": Decimal("25")
            },
            "brazil_europe_coffee": {
                "resource": ResourceType.COFFEE,
                "source": "Brazil", "destination": "Hamburg",
                "transport": "container", "transit_days": 18,
                "cost_per_bag": Decimal("12"),
                "typical_spread": Decimal("18")
            }
        }
    
    def get_live_price(self, resource: ResourceType, location: str) -> Decimal:
        base_prices = {
            ResourceType.CRUDE_OIL: Decimal("78.50"),
            ResourceType.NATURAL_GAS: Decimal("3.20"),
            ResourceType.COPPER: Decimal("8500"),
            ResourceType.LITHIUM: Decimal("15000"),
            ResourceType.WHEAT: Decimal("250"),
            ResourceType.COFFEE: Decimal("180"),
            ResourceType.GOLD: Decimal("2050"),
            ResourceType.URANIUM: Decimal("80")
        }
        
        base = base_prices.get(resource, Decimal("100"))
        adjustments = {"Texas": Decimal("0.95"), "Singapore": Decimal("1.02"),
                      "Shanghai": Decimal("1.03"), "Rotterdam": Decimal("1.01")}
        return base * adjustments.get(location, Decimal("1.0"))
    
    def find_arbitrage_opportunities(self) -> List[Dict]:
        opportunities = []
        
        for route_id, route in self.supply_chains.items():
            resource = route["resource"]
            source_price = self.get_live_price(resource, route["source"])
            dest_price = self.get_live_price(resource, route["destination"])
            
            cost_key = "cost_per_barrel" if resource == ResourceType.CRUDE_OIL else \
                      "cost_per_mmbtu" if resource == ResourceType.NATURAL_GAS else \
                      "cost_per_tonne"
            
            transport_cost = route.get(cost_key, Decimal("50"))
            price_diff = dest_price - source_price
            net_profit = price_diff - transport_cost
            profit_pct = (net_profit / source_price) * 100
            
            if net_profit > 0:
                opportunities.append({
                    "route_id": route_id,
                    "resource": resource.value,
                    "source": route["source"],
                    "destination": route["destination"],
                    "net_profit_per_unit": float(net_profit),
                    "profit_margin_pct": float(profit_pct),
                    "annualized_return_pct": float(profit_pct * (365 / route["transit_days"])),
                    "urgency": "high" if profit_pct > 10 else "medium" if profit_pct > 5 else "low"
                })
        
        return sorted(opportunities, key=lambda x: x["annualized_return_pct"], reverse=True)
    
    def execute_trade(self, route_id: str, quantity: Decimal) -> Dict:
        if route_id not in self.supply_chains:
            return {"success": False, "error": "Unknown route"}
        
        route = self.supply_chains[route_id]
        resource = route["resource"]
        
        source_price = self.get_live_price(resource, route["source"])
        dest_price = self.get_live_price(resource, route["destination"])
        
        cost_key = "cost_per_barrel" if resource == ResourceType.CRUDE_OIL else \
                  "cost_per_mmbtu" if resource == ResourceType.NATURAL_GAS else \
                  "cost_per_tonne"
        
        transport_cost = route.get(cost_key, Decimal("50")) * quantity
        total_cost = (source_price * quantity) + transport_cost
        total_revenue = dest_price * quantity
        net_profit = total_revenue - total_cost
        
        contract_id = f"SCA_{route_id}_{date.today().isoformat()}"
        
        self.active_contracts[contract_id] = ResourceContract(
            contract_id=contract_id, resource_type=resource, quantity=quantity,
            contract_price=source_price, source_location=route["source"],
            destination_location=route["destination"],
            delivery_date=date.today(), transport_cost=transport_cost,
            net_profit=net_profit
        )
        
        self.total_profit += net_profit
        
        return {
            "success": True, "contract_id": contract_id,
            "resource": resource.value, "quantity": float(quantity),
            "net_profit": float(net_profit),
            "profit_margin_pct": float((net_profit / total_cost) * 100),
            "total_contracts": len(self.active_contracts),
            "total_profit_all_time": float(self.total_profit)
        }
    
    def get_portfolio_summary(self) -> Dict:
        if not self.active_contracts:
            return {"total_contracts": 0, "total_profit": 0, "exposure_by_resource": {}}
        
        total_profit = sum(c.net_profit for c in self.active_contracts.values())
        
        by_resource = {}
        for c in self.active_contracts.values():
            r = c.resource_type.value
            by_resource[r] = by_resource.get(r, {"contracts": 0, "profit": 0})
            by_resource[r]["contracts"] += 1
            by_resource[r]["profit"] += float(c.net_profit)
        
        return {
            "total_contracts": len(self.active_contracts),
            "total_unrealized_profit": float(total_profit),
            "total_realized_profit": float(self.total_profit),
            "exposure_by_resource": by_resource,
            "active_routes": list(set(c.source_location + "->" + c.destination_location 
                                     for c in self.active_contracts.values()))
        }
