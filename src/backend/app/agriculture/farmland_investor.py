"""
Farmland Investment Platform
Direct farmland ownership, REITs, agricultural exposure
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class LandType(Enum):
    ROW_CROPS = "row_crops"; ORCHARD = "orchard"; VINEYARD = "vineyard"
    PASTURE = "pasture"; TIMBER = "timber"; MIXED = "mixed"

@dataclass
class FarmlandPlot:
    plot_id: str; location: str; country: str; acres: Decimal
    land_type: LandType; soil_quality: str; water_rights: bool
    purchase_price: Decimal; current_value: Decimal; annual_yield: Decimal
    crops: List[str]; tenant_farmers: List[str]; lease_income_annual: Decimal

class FarmlandInvestor:
    """Invest in physical farmland for income and appreciation"""
    
    def __init__(self):
        self.holdings: Dict[str, FarmlandPlot] = {}
        self.reits: Dict[str, Dict] = {}  # Farmland REITs
    
    def buy_farmland(self, location: str, acres: Decimal, land_type: LandType,
                    price_per_acre: Decimal) -> Dict:
        """Buy physical farmland"""
        total_cost = acres * price_per_acre
        plot_id = f"land_{location.replace(' ', '_').lower()}_{date.today().isoformat()}"
        
        plot = FarmlandPlot(
            plot_id=plot_id, location=location, country="USA", acres=acres,
            land_type=land_type, soil_quality="A", water_rights=True,
            purchase_price=total_cost, current_value=total_cost * Decimal("1.05"),
            annual_yield=Decimal("0.04"),  # 4% annual yield
            crops=["corn", "soybeans"] if land_type == LandType.ROW_CROPS else ["grapes"],
            tenant_farmers=[], lease_income_annual=total_cost * Decimal("0.04")
        )
        self.holdings[plot_id] = plot
        
        return {"success": True, "plot_id": plot_id, "location": location,
                "acres": float(acres), "total_cost_usd": float(total_cost),
                "expected_yield_pct": 4.0, "annual_income_usd": float(plot.lease_income_annual)}
    
    def invest_reit(self, reit_symbol: str, amount_usd: Decimal) -> Dict:
        """Invest in farmland REIT ( Gladstone Land - LAND, Farmland Partners - FPI )"""
        reit_data = {
            "LAND": {"name": "Gladstone Land", "dividend_yield": 3.8, "focus": "specialty crops"},
            "FPI": {"name": "Farmland Partners", "dividend_yield": 2.9, "focus": "row crops"},
            "IAF": {"name": " iAgriculture Fund", "dividend_yield": 3.5, "focus": "global farms"}
        }
        
        info = reit_data.get(reit_symbol, {"name": "Unknown", "dividend_yield": 3.0, "focus": "mixed"})
        shares = amount_usd / Decimal("20")  # Assume $20/share
        annual_dividend = amount_usd * Decimal(str(info["dividend_yield"] / 100))
        
        self.reits[reit_symbol] = {"shares": float(shares), "cost_basis": float(amount_usd),
                                   "annual_dividend": float(annual_dividend)}
        
        return {"success": True, "reit": reit_symbol, "name": info["name"],
                "shares": float(shares), "annual_dividend_usd": float(annual_dividend),
                "dividend_yield_pct": info["dividend_yield"]}
    
    def get_portfolio(self) -> Dict:
        """Get farmland investment portfolio"""
        total_land_value = sum(p.current_value for p in self.holdings.values())
        total_reit_value = sum(r["cost_basis"] for r in self.reits.values())
        total_annual_income = sum(p.lease_income_annual for p in self.holdings.values())
        total_annual_income += sum(Decimal(str(r["annual_dividend"])) for r in self.reits.values())
        
        return {"total_value_usd": float(total_land_value + Decimal(str(total_reit_value))),
                "physical_land_usd": float(total_land_value),
                "reits_usd": float(total_reit_value),
                "annual_income_usd": float(total_annual_income),
                "income_yield_pct": float(total_annual_income / (total_land_value + Decimal(str(total_reit_value))) * 100) if (total_land_value + Decimal(str(total_reit_value))) > 0 else 0,
                "land_holdings": [{"id": p.plot_id, "location": p.location, "acres": float(p.acres),
                                  "type": p.land_type.value, "value": float(p.current_value)} for p in self.holdings.values()],
                "reit_holdings": [{"symbol": s, "shares": r["shares"], "dividend": r["annual_dividend"]} for s, r in self.reits.items()]}
