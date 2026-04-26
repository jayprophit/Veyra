"""
Precious Metals Trading System
Physical gold, silver, platinum, palladium trading
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class MetalType(Enum):
    GOLD = "gold"; SILVER = "silver"; PLATINUM = "platinum"
    PALLADIUM = "palladium"; RHODIUM = "rhodium"; COPPER = "copper"

class StorageLocation(Enum):
    LONDON = "london"; NEW_YORK = "new_york"; ZURICH = "zurich"
    SINGAPORE = "singapore"; DUBAI = "dubai"; HOME_DELIVERY = "home"

@dataclass
class MetalHolding:
    holding_id: str; metal_type: MetalType; quantity_oz: Decimal
    storage_location: StorageLocation; vault_provider: str
    avg_cost_per_oz: Decimal; current_value: Decimal
    unrealized_pnl: Decimal; allocated: bool = True

@dataclass  
class MetalPrice:
    metal_type: MetalType; spot_usd: Decimal; bid_usd: Decimal
    ask_usd: Decimal; timestamp: datetime

class MetalsTrader:
    """Physical precious metals trading platform"""
    
    def __init__(self):
        self.holdings: Dict[str, MetalHolding] = {}
        self.prices: Dict[MetalType, MetalPrice] = {}
    
    async def buy_metal(self, metal: MetalType, quantity_oz: Decimal,
                       storage: StorageLocation) -> Dict:
        """Buy physical metal with vault storage"""
        price = Decimal("2050") if metal == MetalType.GOLD else Decimal("25.50")
        base_cost = quantity_oz * price
        premium = base_cost * Decimal("0.02")  # 2% premium
        total_cost = base_cost + premium
        
        holding_id = f"{metal.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        holding = MetalHolding(
            holding_id=holding_id, metal_type=metal, quantity_oz=quantity_oz,
            storage_location=storage, vault_provider="Brink's London",
            avg_cost_per_oz=total_cost/quantity_oz, current_value=base_cost,
            unrealized_pnl=-premium
        )
        self.holdings[holding_id] = holding
        
        return {"success": True, "holding_id": holding_id, 
                "metal": metal.value, "quantity_oz": float(quantity_oz),
                "total_cost_usd": float(total_cost), "storage": storage.value}
    
    async def sell_metal(self, holding_id: str, quantity_oz: Optional[Decimal] = None) -> Dict:
        """Sell physical metal from vault"""
        if holding_id not in self.holdings:
            return {"success": False, "error": "Holding not found"}
        
        holding = self.holdings[holding_id]
        sell_qty = quantity_oz or holding.quantity_oz
        
        price = Decimal("2050") if holding.metal_type == MetalType.GOLD else Decimal("25.50")
        proceeds = sell_qty * price * Decimal("0.995")  # 0.5% selling fee
        cost_basis = sell_qty * holding.avg_cost_per_oz
        pnl = proceeds - cost_basis
        
        if sell_qty >= holding.quantity_oz:
            del self.holdings[holding_id]
        else:
            holding.quantity_oz -= sell_qty
        
        return {"success": True, "holding_id": holding_id,
                "net_proceeds_usd": float(proceeds), "realized_pnl_usd": float(pnl)}
    
    def get_portfolio_summary(self) -> Dict:
        """Get all metal holdings summary"""
        if not self.holdings:
            return {"total_value_usd": 0, "holdings_count": 0, "holdings": []}
        
        total_value = sum(h.current_value for h in self.holdings.values())
        total_pnl = sum(h.unrealized_pnl for h in self.holdings.values())
        
        by_metal = {}
        for h in self.holdings.values():
            m = h.metal_type.value
            by_metal[m] = by_metal.get(m, {"oz": 0, "usd": 0})
            by_metal[m]["oz"] += float(h.quantity_oz)
            by_metal[m]["usd"] += float(h.current_value)
        
        return {"total_value_usd": float(total_value), 
                "total_unrealized_pnl_usd": float(total_pnl),
                "holdings_count": len(self.holdings), "by_metal": by_metal,
                "holdings": [{"id": h.holding_id, "metal": h.metal_type.value,
                             "oz": float(h.quantity_oz), "vault": h.vault_provider,
                             "value": float(h.current_value)} for h in self.holdings.values()]}
